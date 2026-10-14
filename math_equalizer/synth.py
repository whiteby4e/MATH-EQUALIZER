from __future__ import annotations

import threading
from collections import deque

import numpy as np
import sounddevice as sd

from .formula import SafeFormula


def synthesize_formula(formula: SafeFormula, start_sample: int, count: int,
                       sample_rate: int) -> np.ndarray:
    """Generate a mono float32 block by evaluating the formula over sample times."""
    if count <= 0:
        return np.zeros(0, dtype=np.float32)
    times = (start_sample + np.arange(count, dtype=np.float64)) / float(sample_rate)
    values = formula.evaluate(times)
    return np.clip(values, -1.0, 1.0).astype(np.float32, copy=False)


class FormulaSynthProcessor:
    """Callback-based synthesis engine with a bounded playback pass."""

    def __init__(self, formula: SafeFormula, low_power: bool = False,
                 duration: float = 30.0):
        self.sample_rate = 22050 if low_power else 44100
        self.channels = 1
        self.low_power = low_power
        self.duration = max(1.0, min(float(duration), 300.0))
        self.total_samples = int(self.sample_rate * self.duration)
        self.formula = formula
        self.position = 0
        self.playing = False
        self.finished = False
        self.error = None
        self._stream = None
        self._lock = threading.RLock()
        self._recent_output = deque(maxlen=8)
        self._blocksize = 1024 if low_power else 512

    @property
    def current_time(self):
        return min(self.position / float(self.sample_rate), self.duration)

    def set_formula(self, formula):
        with self._lock:
            self.formula = formula
            self.error = None

    def callback(self, outdata, frames, time_info, status):
        with self._lock:
            if not self.playing:
                outdata.fill(0)
                return
            remaining = self.total_samples - self.position
            count = min(frames, max(0, remaining))
            outdata.fill(0)
            if count:
                try:
                    block = synthesize_formula(
                        self.formula, self.position, count, self.sample_rate
                    )
                except Exception as exc:
                    self.error = str(exc)
                    self.playing = False
                    return
                outdata[:count, 0] = block
                self.position += count
                self._recent_output.append(block.copy())
            if self.position >= self.total_samples:
                self.finished = True
                self.playing = False

    def start(self):
        with self._lock:
            if self.finished:
                self.position = 0
                self.finished = False
                self._recent_output.clear()
            if self._stream is None:
                self._stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32",
                    callback=self.callback,
                    blocksize=self._blocksize,
                    latency="low",
                )
                self._stream.start()
            elif not self._stream.active:
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
            self.error = None
            self._recent_output.clear()

    def get_recent_output(self, samples=4096):
        with self._lock:
            if not self._recent_output:
                return None
            data = np.concatenate(list(self._recent_output))
        return data[-samples:].reshape(-1, 1).copy()

    def close(self):
        with self._lock:
            self.playing = False
            if self._stream is not None:
                try:
                    self._stream.stop()
                finally:
                    self._stream.close()
                    self._stream = None
