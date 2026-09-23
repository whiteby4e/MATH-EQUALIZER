from __future__ import annotations

import numpy as np
from .qt_compat import LEGACY_WINDOWS

if LEGACY_WINDOWS:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
else:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Visualizer(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 5), tight_layout=True)
        super().__init__(self.figure)
        self.setParent(parent)
        self.ax_formula = self.figure.add_subplot(211)
        self.ax_fft = self.figure.add_subplot(212)
        self.formula_line, = self.ax_formula.plot([], [])
        self.spectrum_line, = self.ax_fft.plot([], [])
        self.ax_formula.set_title("Mathematical Formula")
        self.ax_formula.set_xlabel("Time (seconds)")
        self.ax_formula.set_ylabel("Gain")
        self.ax_formula.grid(True, alpha=0.2)
        self.ax_fft.set_title("Output FFT Spectrum")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Magnitude (dB)")
        self.ax_fft.set_xlim(0, 12000)
        self.ax_fft.set_ylim(-80, 2)
        self.ax_fft.grid(True, alpha=0.2)

    def update_formula(self, formula, current_time):
        t = np.linspace(current_time, current_time + 4.0, 600)
        try: y = formula.evaluate(t)
        except Exception: y = np.ones_like(t)
        y = np.clip(y, -5, 5)
        self.formula_line.set_data(t, y)
        self.ax_formula.set_xlim(t[0], t[-1])
        self.ax_formula.set_ylim(min(-1.2, float(np.min(y)) - 0.2), max(1.2, float(np.max(y)) + 0.2))

    def update_spectrum(self, samples, sample_rate):
        if samples is None or len(samples) < 32: return
        x = np.asarray(samples, dtype=np.float64)
        if x.ndim > 1: x = np.mean(x, axis=1)
        n = min(4096, len(x)); x = x[-n:]
        spectrum = np.abs(np.fft.rfft(x * np.hanning(n)))
        freqs = np.fft.rfftfreq(n, 1.0 / sample_rate)
        keep = freqs <= min(12000, sample_rate / 2)
        spectrum, freqs = spectrum[keep], freqs[keep]
        magnitude = 20 * np.log10(np.maximum(spectrum, 1e-8))
        if len(magnitude): magnitude -= np.max(magnitude)
        self.spectrum_line.set_data(freqs, magnitude)
        self.ax_fft.set_xlim(0, min(12000, sample_rate / 2)); self.ax_fft.set_ylim(-80, 2)

    def refresh(self): self.draw_idle()
