"""Procedural, original retro-synth Easter egg for MATH-EQUALIZER.

This creates a short original tune from oscillators; it does not load audio files
or reproduce a copyrighted song melody.
"""
from __future__ import annotations

import numpy as np


def make_mathroll(sample_rate: int = 22050, duration: float = 8.0) -> np.ndarray:
    """Return a stereo, normalized, original retro-pop synth tune."""
    sr = max(8000, int(sample_rate))
    duration = max(2.0, min(float(duration), 12.0))
    count = int(sr * duration)
    t = np.arange(count, dtype=np.float64) / sr
    audio = np.zeros(count, dtype=np.float64)

    # Original sequence in A minor; deliberately not based on a known song.
    notes = [57, 60, 64, 67, 64, 62, 59, 55, 57, 64, 69, 67, 62, 59, 60, 57]
    beat = 0.25
    for index, midi in enumerate(notes):
        start = int(index * beat * sr)
        end = min(count, start + int(beat * sr * 0.92))
        if end <= start:
            continue
        local_t = np.arange(end - start, dtype=np.float64) / sr
        freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        envelope = np.minimum(1.0, local_t * 45.0) * np.exp(-local_t * 3.0)
        tone = (
            0.68 * np.sin(2.0 * np.pi * freq * local_t)
            + 0.22 * np.sin(2.0 * np.pi * freq * 2.0 * local_t)
            + 0.10 * np.sign(np.sin(2.0 * np.pi * freq * local_t))
        )
        audio[start:end] += tone * envelope * 0.22

    # Simple pulsing bass and a quiet synthetic kick on each bar beat.
    for beat_index in range(int(duration / 0.5)):
        start = int(beat_index * 0.5 * sr)
        end = min(count, start + int(0.42 * sr))
        if end <= start:
            continue
        local_t = np.arange(end - start, dtype=np.float64) / sr
        bass_midi = [45, 41, 43, 40][(beat_index // 2) % 4]
        bass_freq = 440.0 * (2.0 ** ((bass_midi - 69) / 12.0))
        audio[start:end] += (
            0.12 * np.sin(2.0 * np.pi * bass_freq * local_t)
            * np.exp(-local_t * 5.0)
        )
        if beat_index % 2 == 0:
            kick_freq = 95.0 - 45.0 * np.minimum(local_t / 0.16, 1.0)
            phase = 2.0 * np.pi * np.cumsum(kick_freq) / sr
            audio[start:end] += 0.10 * np.sin(phase) * np.exp(-local_t * 18.0)

    fade = min(int(sr * 0.04), count // 2)
    if fade:
        audio[:fade] *= np.linspace(0.0, 1.0, fade)
        audio[-fade:] *= np.linspace(1.0, 0.0, fade)

    peak = float(np.max(np.abs(audio))) if count else 0.0
    if peak > 0.0:
        audio *= 0.78 / peak

    # Slight stereo spread without adding any external dependencies.
    stereo = np.column_stack((audio, np.roll(audio, int(sr * 0.004)) * 0.96))
    return stereo.astype(np.float32)
