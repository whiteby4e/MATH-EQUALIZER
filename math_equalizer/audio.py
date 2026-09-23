from __future__ import annotations

import sys
import threading
from collections import deque
from dataclasses import dataclass

import numpy as np
import sounddevice as sd
import soundfile as sf


@dataclass
class AudioInfo:
    sample_rate: int
    channels: int
    frames: int
    duration: float


class RealTimeProcessor:

    def __init__(
        self,
        audio: np.ndarray,
        sample_rate: int,
        low_power: bool = False
    ):
        if audio.ndim == 1:
            audio = audio[:, None]

        self.audio = np.asarray(
            audio,
            dtype=np.float32
        )

        self.sample_rate = int(sample_rate)
        self.channels = self.audio.shape[1]
        self.low_power = low_power

        # Smaller FFT + no overlap in Low Power Mode reduces CPU usage.
        self.fft_size = 1024 if low_power else 2048
        self.hop = 1024 if low_power else 512

        self.window = np.sqrt(
            np.hanning(self.fft_size)
        ).astype(np.float64)

        self.freqs = np.fft.rfftfreq(
            self.fft_size,
            1.0 / self.sample_rate
        )

        self.position = 0

        self.out_buffer = np.zeros(
            (0, self.channels),
            dtype=np.float32
        )

        self.ola = np.zeros(
            (
                self.fft_size + self.hop,
                self.channels
            ),
            dtype=np.float64
        )

        self.ola_weight = np.zeros(
            self.fft_size + self.hop,
            dtype=np.float64
        )

        self.formula = None
        self.band = "BASS"

        self.playing = False
        self.finished = False

        self._stream = None
        self._lock = threading.RLock()

        self._recent_output = deque(
            maxlen=16
        )

    @property
    def duration(self):
        return len(self.audio) / self.sample_rate

    @property
    def current_time(self):
        return min(
            self.position / self.sample_rate,
            self.duration
        )

    def set_formula(self, formula):
        with self._lock:
            self.formula = formula

    def set_band(self, band):
        with self._lock:
            self.band = band.upper()

    def _band_mask(self):

        if self.band == "BASS":
            return self.freqs < 250.0

        if self.band == "MID":
            return (
                (self.freqs >= 250.0)
                &
                (self.freqs < 4000.0)
            )

        if self.band == "TREBLE":
            return self.freqs >= 4000.0

        return np.ones(
            len(self.freqs),
            dtype=bool
        )

    def _get_gain(self, time_seconds):

        if self.formula is None:
            return 1.0

        try:
            value = self.formula.scalar(
                time_seconds
            )
        except Exception:
            return 1.0

        return float(
            np.clip(
                value,
                0.0,
                3.0
            )
        )

    def _process_frame(
        self,
        frame,
        time_seconds
    ):

        x = (
            frame.astype(np.float64)
            *
            self.window[:, None]
        )

        spectrum = np.fft.rfft(
            x,
            axis=0
        )

        gain = self._get_gain(
            time_seconds
        )

        mask = self._band_mask()

        spectrum[mask] *= gain

        y = np.fft.irfft(
            spectrum,
            n=self.fft_size,
            axis=0
        )

        y *= self.window[:, None]

        return y

    def _append_processed_block(self):

        start = self.position

        end = min(
            start + self.fft_size,
            len(self.audio)
        )

        frame = np.zeros(
            (
                self.fft_size,
                self.channels
            ),
            dtype=np.float64
        )

        if end > start:
            frame[
                :end - start
            ] = self.audio[start:end]

        if start < len(self.audio):
            center_time = (
                start
                +
                self.fft_size / 2
            ) / self.sample_rate

            processed = self._process_frame(
                frame,
                center_time
            )
        else:
            processed = (
                frame
                *
                self.window[:, None]
                *
                self.window[:, None]
            )

        self.ola[:self.fft_size] += processed

        self.ola_weight[:self.fft_size] += (
            self.window ** 2
        )

        usable = self.hop

        denominator = np.maximum(
            self.ola_weight[:usable],
            1e-8
        )

        output = (
            self.ola[:usable]
            /
            denominator[:, None]
        )

        output = np.clip(
            output,
            -1.0,
            1.0
        ).astype(np.float32)

        self.out_buffer = np.vstack(
            (
                self.out_buffer,
                output
            )
        )

        self._recent_output.append(
            output.copy()
        )

        self.ola[:-self.hop] = (
            self.ola[self.hop:]
        )

        self.ola[-self.hop:] = 0.0

        self.ola_weight[:-self.hop] = (
            self.ola_weight[self.hop:]
        )

        self.ola_weight[-self.hop:] = 0.0

        self.position += self.hop

        if self.position >= (
            len(self.audio)
            +
            self.fft_size
        ):
            self.finished = True

    def callback(
        self,
        outdata,
        frames,
        time,
        status
    ):

        if status:
            print(
                status,
                file=sys.stderr
            )

        with self._lock:

            if not self.playing:
                outdata.fill(0)
                return

            while (
                len(self.out_buffer) < frames
                and not self.finished
            ):
                self._append_processed_block()

            n = min(
                frames,
                len(self.out_buffer)
            )

            if n > 0:
                outdata[:n] = (
                    self.out_buffer[:n]
                )

                self.out_buffer = (
                    self.out_buffer[n:]
                )

            if n < frames:
                outdata[n:].fill(0)

                if self.finished:
                    self.playing = False

    def start(self):

        with self._lock:

            if self.finished:
                self.position = 0
                self.finished = False
                self.out_buffer = np.zeros(
                    (
                        0,
                        self.channels
                    ),
                    dtype=np.float32
                )

                self.ola.fill(0)
                self.ola_weight.fill(0)

            if self._stream is None:

                self._stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype="float32",
                    callback=self.callback,
                    blocksize=self.hop,
                    latency="low"
                )

                self._stream.start()

            self.playing = True

    def pause(self):

        with self._lock:
            self.playing = False

    def stop(self):

        with self._lock:

            self.playing = False

            self.position = 0
            self.finished = False

            self.out_buffer = np.zeros(
                (
                    0,
                    self.channels
                ),
                dtype=np.float32
            )

            self.ola.fill(0)
            self.ola_weight.fill(0)

            self._recent_output.clear()

    def get_recent_output(
        self,
        samples=4096
    ):

        with self._lock:

            if not self._recent_output:
                return None

            chunks = list(
                self._recent_output
            )

        data = np.concatenate(
            chunks,
            axis=0
        )

        if len(data) > samples:
            data = data[-samples:]

        return data.copy()

    def close(self):

        with self._lock:

            self.playing = False

            if self._stream is not None:
                try:
                    self._stream.stop()
                finally:
                    self._stream.close()

                self._stream = None


def load_audio(path: str):

    data, sr = sf.read(
        path,
        dtype="float32",
        always_2d=True
    )

    if data.size == 0:
        raise ValueError(
            "The selected audio file is empty."
        )

    peak = float(
        np.max(np.abs(data))
    )

    if peak > 1.0:
        data = data / peak

    info = AudioInfo(
        sample_rate=int(sr),
        channels=int(data.shape[1]),
        frames=int(data.shape[0]),
        duration=float(
            data.shape[0] / sr
        )
    )

    return data, info