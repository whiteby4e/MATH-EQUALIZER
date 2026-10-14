from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from .qt_compat import (
    QApplication, QFileDialog, QComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QTimer, Qt, QVBoxLayout, QWidget, exec_app,
)
from .audio import RealTimeProcessor, load_audio
from .formula import FormulaError, SafeFormula
from .synth import FormulaSynthProcessor


FILE_FORMULA = "1 + 0.5*sin(2*pi*2*t)"
SYNTH_FORMULA = "sin(2*pi*440*t)"


class LightweightVisualizer:
    def update_formula(self, formula, current_time):
        return None

    def update_spectrum(self, samples, sample_rate):
        return None

    def refresh(self):
        return None


class MainWindow(QMainWindow):
    def __init__(self, low_power=False):
        super().__init__()
        self.low_power = low_power
        self.setWindowTitle("MATH-EQUALIZER • Formula Audio")
        self.resize(680 if low_power else 760, 470 if low_power else 590)
        self.processor = None
        self.audio = None
        self.audio_sample_rate = None
        self.sample_rate = None
        self.audio_path = None
        self.formula = SafeFormula(FILE_FORMULA)
        self._build_ui()
        self.timer = QTimer(self)
        self.timer.setInterval(250 if self.low_power else 100)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(7)

        title = QLabel("MATH-EQUALIZER")
        title.setStyleSheet("font-size: 21px; font-weight: bold;")
        root.addWidget(title)
        subtitle = QLabel("A compact calculator for mathematical audio.")
        subtitle.setStyleSheet("color: #777;")
        root.addWidget(subtitle)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Process an audio file", "Generate sound from formula"])
        self.mode_combo.currentTextChanged.connect(self._mode_changed)
        mode_row.addWidget(self.mode_combo, 1)
        root.addLayout(mode_row)

        self.audio_box = QGroupBox("Input audio")
        audio_layout = QHBoxLayout(self.audio_box)
        self.choose_button = QPushButton("Choose file…")
        self.choose_button.clicked.connect(self.choose_audio)
        audio_layout.addWidget(self.choose_button)
        self.file_label = QLabel("No audio selected")
        self.file_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        audio_layout.addWidget(self.file_label, 1)
        root.addWidget(self.audio_box)

        self.math_box = QGroupBox("Formula")
        form = QFormLayout(self.math_box)
        self.formula_edit = QLineEdit(FILE_FORMULA)
        self.formula_edit.setPlaceholderText("Example: sin(2*pi*440*t)")
        self.formula_edit.returnPressed.connect(self.apply_formula)
        self.formula_edit.setStyleSheet("font-family: Consolas, monospace; font-size: 14px; padding: 8px;")
        form.addRow("Expression", self.formula_edit)

        keypad = QHBoxLayout()
        for token in ("sin(", "cos(", "pi", "t", "**", "sqrt(", "abs("):
            key = QPushButton(token)
            key.setToolTip("Insert " + token)
            key.clicked.connect(lambda checked=False, value=token: self.formula_edit.insert(value))
            keypad.addWidget(key)
        clear_key = QPushButton("C")
        clear_key.setToolTip("Clear formula")
        clear_key.clicked.connect(self.formula_edit.clear)
        keypad.addWidget(clear_key)
        form.addRow("Keys", keypad)

        self.band_combo = QComboBox()
        self.band_combo.addItems(["BASS", "MID", "TREBLE", "FULL"])
        self.band_combo.currentTextChanged.connect(self.change_band)
        self.band_label = QLabel("Apply to")
        form.addRow(self.band_label, self.band_combo)

        self.help_text = QLabel("t = time in seconds • sin, cos, tan, exp, sqrt, abs, log, log10, pi, e")
        self.help_text.setWordWrap(True)
        self.help_text.setStyleSheet("color: #777;")
        form.addRow("", self.help_text)
        root.addWidget(self.math_box)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: 600; padding: 4px;")
        root.addWidget(self.status_label)

        if self.low_power:
            self.visualizer = LightweightVisualizer()
            note = QLabel("Low Power: graphs disabled • 22.05 kHz synthesis • slower UI refresh")
            note.setStyleSheet("color: #777;")
            root.addWidget(note)
        else:
            from .visualizer import Visualizer
            self.visualizer = Visualizer()
            root.addWidget(self.visualizer, 1)

        buttons = QHBoxLayout()
        self.play_button = QPushButton("▶ Generate / Play")
        self.play_button.clicked.connect(self.play_pause)
        buttons.addWidget(self.play_button)
        self.stop_button = QPushButton("■ Stop")
        self.stop_button.clicked.connect(self.stop)
        buttons.addWidget(self.stop_button)
        self.apply_button = QPushButton("Apply formula")
        self.apply_button.clicked.connect(self.apply_formula)
        buttons.addWidget(self.apply_button)
        root.addLayout(buttons)

        self.setStyleSheet(
            "QGroupBox { font-weight: 600; margin-top: 5px; padding-top: 8px; }"
            "QPushButton { padding: 6px 9px; }"
            "QLineEdit, QComboBox { padding: 5px; }"
        )

    def _is_synth_mode(self):
        return self.mode_combo.currentIndex() == 1

    def _mode_changed(self, _text):
        if self.processor:
            self.processor.close()
            self.processor = None
        if self._is_synth_mode():
            if self.formula_edit.text().strip() == FILE_FORMULA:
                self.formula_edit.setText(SYNTH_FORMULA)
            self.audio_box.hide()
            self.band_combo.hide()
            self.band_label.hide()
            self.help_text.setText(
                "Output = formula(t) • t is time in seconds • values are clipped to -1…1"
            )
            self.play_button.setText("▶ Generate / Play")
            self.status_label.setText("Enter a formula, then Generate / Play.")
        else:
            if self.formula_edit.text().strip() == SYNTH_FORMULA:
                self.formula_edit.setText(FILE_FORMULA)
            self.audio_box.show()
            self.band_combo.show()
            self.band_label.show()
            self.help_text.setText(
                "t = time in seconds • sin, cos, tan, exp, sqrt, abs, log, log10, pi, e"
            )
            if self.audio is not None and self.audio_sample_rate is not None:
                self.processor = RealTimeProcessor(
                    self.audio, self.audio_sample_rate, low_power=self.low_power
                )
                self.sample_rate = self.audio_sample_rate
                self.processor.set_formula(self.formula)
                self.processor.set_band(self.band_combo.currentText())
            self.play_button.setText("▶ Play")
            self.status_label.setText(
                "Audio loaded. Press Play." if self.audio is not None
                else "Choose an audio file to begin."
            )

    def choose_audio(self):
        if self._is_synth_mode():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose audio", "",
            "Audio files (*.wav *.aiff *.aif *.flac *.ogg);;All files (*.*)"
        )
        if not path:
            return
        try:
            if self.processor:
                self.processor.close()
                self.processor = None
            audio, info = load_audio(path)
            self.audio, self.audio_sample_rate = audio, info.sample_rate
            self.sample_rate, self.audio_path = info.sample_rate, Path(path)
            self.processor = RealTimeProcessor(audio, info.sample_rate, low_power=self.low_power)
            self.processor.set_formula(self.formula)
            self.processor.set_band(self.band_combo.currentText())
            self.file_label.setText(
                f"{self.audio_path.name} • {info.duration:.1f}s • "
                f"{info.sample_rate} Hz • {info.channels} ch"
            )
            self.status_label.setText("Audio loaded. Press Play.")
            self.play_button.setText("▶ Play")
        except Exception as exc:
            QMessageBox.critical(self, "Could not load audio", str(exc))

    def apply_formula(self):
        text = self.formula_edit.text().strip()
        try:
            formula = SafeFormula(text)
            probe = np.array([0.0, 0.001, 0.01]) if self._is_synth_mode() else np.array([0.0, 0.5, 1.0])
            formula.evaluate(probe)
        except (FormulaError, ValueError, FloatingPointError) as exc:
            QMessageBox.warning(self, "Invalid formula", str(exc))
            return False
        self.formula = formula
        if self.processor:
            self.processor.set_formula(formula)
        self.status_label.setText(
            "Synthesis formula ready." if self._is_synth_mode()
            else f"Formula active: {text}"
        )
        return True

    def change_band(self, band):
        if self.processor and not self._is_synth_mode():
            self.processor.set_band(band)
        if not self._is_synth_mode():
            self.status_label.setText(f"Band: {band}")

    def play_pause(self):
        if self._is_synth_mode():
            if not self.apply_formula():
                return
            if self.processor is None:
                try:
                    self.processor = FormulaSynthProcessor(
                        self.formula, low_power=self.low_power
                    )
                    self.sample_rate = self.processor.sample_rate
                except Exception as exc:
                    QMessageBox.critical(self, "Could not prepare synthesis", str(exc))
                    return
        elif self.processor is None:
            QMessageBox.information(self, "No audio", "Choose an audio file first.")
            return

        if self.processor.playing:
            self.processor.pause()
            self.play_button.setText("▶ Resume")
            self.status_label.setText("Paused")
        else:
            try:
                self.processor.start()
                self.play_button.setText("Ⅱ Pause")
                self.status_label.setText("Generating sound…" if self._is_synth_mode() else "Playing")
            except Exception as exc:
                QMessageBox.critical(self, "Audio output error", str(exc))

    def stop(self):
        if self.processor:
            self.processor.stop()
            self.play_button.setText("▶ Generate / Play" if self._is_synth_mode() else "▶ Play")
            self.status_label.setText("Stopped")

    def _tick(self):
        if not self.processor:
            return
        position = self.processor.current_time
        self.visualizer.update_formula(self.formula, position)
        recent = self.processor.get_recent_output(4096)
        if recent is not None and self.sample_rate:
            self.visualizer.update_spectrum(recent, self.sample_rate)
        self.visualizer.refresh()
        if getattr(self.processor, "error", None):
            self.status_label.setText("Formula error: " + self.processor.error)
            self.processor.pause()
            self.play_button.setText("▶ Resume")
        elif self.processor.finished and not self.processor.playing:
            self.play_button.setText("▶ Generate again" if self._is_synth_mode() else "▶ Play")
            self.status_label.setText("Finished")

    def closeEvent(self, event):
        self.timer.stop()
        if self.processor:
            self.processor.close()
            self.processor = None
        event.accept()


def run():
    low_power = "--low-power" in sys.argv or "-L" in sys.argv
    app = QApplication(sys.argv)
    window = MainWindow(low_power=low_power)
    window.show()
    sys.exit(exec_app(app))
