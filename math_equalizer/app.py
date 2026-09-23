from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from PySide6.QtCore import (
    QTimer,
    Qt
)

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from .audio import (
    RealTimeProcessor,
    load_audio
)

from .formula import (
    FormulaError,
    SafeFormula
)

from .visualizer import (
    Visualizer
)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Math Equalizer v0.1"
        )

        self.resize(
            1100,
            800
        )

        self.processor = None
        self.audio = None
        self.sample_rate = None
        self.audio_path = None

        self.formula = SafeFormula("1")

        self._build_ui()

        self.timer = QTimer(self)

        self.timer.setInterval(50)

        self.timer.timeout.connect(
            self._tick
        )

        self.timer.start()

    def _build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        root = QVBoxLayout(
            central
        )

        title = QLabel(
            "MATH EQUALIZER"
        )

        title.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            """
        )

        root.addWidget(title)

        subtitle = QLabel(
            "Change audio using mathematics in real time."
        )

        subtitle.setStyleSheet(
            "color: #777;"
        )

        root.addWidget(
            subtitle
        )

        audio_box = QGroupBox(
            "Audio"
        )

        audio_layout = QHBoxLayout(
            audio_box
        )

        self.choose_button = (
            QPushButton(
                "Choose audio..."
            )
        )

        self.choose_button.clicked.connect(
            self.choose_audio
        )

        audio_layout.addWidget(
            self.choose_button
        )

        self.file_label = QLabel(
            "No audio selected"
        )

        self.file_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        audio_layout.addWidget(
            self.file_label,
            1
        )

        root.addWidget(
            audio_box
        )

        math_box = QGroupBox(
            "Mathematical Control"
        )

        form = QFormLayout(
            math_box
        )

        self.formula_edit = QLineEdit(
            "1 + 0.5*sin(2*pi*2*t)"
        )

        self.formula_edit.setPlaceholderText(
            "Example: 1 + 0.5*sin(2*pi*2*t)"
        )

        self.formula_edit.returnPressed.connect(
            self.apply_formula
        )

        form.addRow(
            "Formula:",
            self.formula_edit
        )

        self.band_combo = QComboBox()

        self.band_combo.addItems(
            [
                "BASS",
                "MID",
                "TREBLE",
                "FULL"
            ]
        )

        self.band_combo.currentTextChanged.connect(
            self.change_band
        )

        form.addRow(
            "Apply to:",
            self.band_combo
        )

        help_text = QLabel(
            "t, pi, e, sin, cos, tan, exp, sqrt, "
            "abs, log, log10, floor, ceil"
        )

        help_text.setStyleSheet(
            "color: #777;"
        )

        form.addRow(
            "",
            help_text
        )

        root.addWidget(
            math_box
        )

        self.status_label = QLabel(
            "Ready"
        )

        root.addWidget(
            self.status_label
        )

        self.visualizer = Visualizer()

        root.addWidget(
            self.visualizer,
            1
        )

        buttons = QHBoxLayout()

        self.play_button = QPushButton(
            "▶ Play"
        )

        self.play_button.clicked.connect(
            self.play_pause
        )

        buttons.addWidget(
            self.play_button
        )

        self.stop_button = QPushButton(
            "■ Stop"
        )

        self.stop_button.clicked.connect(
            self.stop
        )

        buttons.addWidget(
            self.stop_button
        )

        self.apply_button = QPushButton(
            "Apply Formula"
        )

        self.apply_button.clicked.connect(
            self.apply_formula
        )

        buttons.addWidget(
            self.apply_button
        )

        buttons.addStretch()

        root.addLayout(
            buttons
        )

        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                margin-top: 10px;
                padding-top: 12px;
            }

            QPushButton {
                padding: 8px 14px;
            }

            QLineEdit,
            QComboBox {
                padding: 7px;
            }
            """
        )

    def choose_audio(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose audio",
            "",
            (
                "Audio files "
                "(*.wav *.aiff *.aif *.flac *.ogg);;"
                "All files (*.*)"
            )
        )

        if not path:
            return

        try:

            if self.processor:
                self.processor.close()

            audio, info = load_audio(
                path
            )

            self.audio = audio
            self.sample_rate = (
                info.sample_rate
            )

            self.audio_path = Path(
                path
            )

            self.processor = (
                RealTimeProcessor(
                    audio,
                    info.sample_rate
                )
            )

            self.processor.set_formula(
                self.formula
            )

            self.processor.set_band(
                self.band_combo.currentText()
            )

            self.file_label.setText(
                f"{self.audio_path.name} • "
                f"{info.duration:.1f}s • "
                f"{info.sample_rate} Hz • "
                f"{info.channels} ch"
            )

            self.status_label.setText(
                "Audio loaded. Press Play."
            )

            self.play_button.setText(
                "▶ Play"
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Could not load audio",
                str(exc)
            )

    def apply_formula(self):

        text = (
            self.formula_edit
            .text()
            .strip()
        )

        try:

            formula = SafeFormula(
                text
            )

            formula.evaluate(
                np.array(
                    [
                        0.0,
                        0.5,
                        1.0
                    ]
                )
            )

        except FormulaError as exc:

            QMessageBox.warning(
                self,
                "Invalid formula",
                str(exc)
            )

            return

        self.formula = formula

        if self.processor:
            self.processor.set_formula(
                formula
            )

        self.status_label.setText(
            f"Formula active: {text}"
        )

    def change_band(self, band):

        if self.processor:
            self.processor.set_band(
                band
            )

        self.status_label.setText(
            f"Band: {band}"
        )

    def play_pause(self):

        if not self.processor:

            QMessageBox.information(
                self,
                "No audio",
                "Choose an audio file first."
            )

            return

        if self.processor.playing:

            self.processor.pause()

            self.play_button.setText(
                "▶ Play"
            )

            self.status_label.setText(
                "Paused"
            )

        else:

            try:

                self.processor.start()

                self.play_button.setText(
                    "Ⅱ Pause"
                )

                self.status_label.setText(
                    "Playing"
                )

            except Exception as exc:

                QMessageBox.critical(
                    self,
                    "Audio output error",
                    str(exc)
                )

    def stop(self):

        if self.processor:

            self.processor.stop()

            self.play_button.setText(
                "▶ Play"
            )

            self.status_label.setText(
                "Stopped"
            )

    def _tick(self):

        if not self.processor:
            return

        position = (
            self.processor.current_time
        )

        self.visualizer.update_formula(
            self.formula,
            position
        )

        recent = (
            self.processor
            .get_recent_output(4096)
        )

        if recent is not None:

            self.visualizer.update_spectrum(
                recent,
                self.sample_rate
            )

        self.visualizer.refresh()

        if (
            self.processor.finished
            and
            not self.processor.playing
        ):

            self.play_button.setText(
                "▶ Play"
            )

            self.status_label.setText(
                "Finished"
            )

    def closeEvent(self, event):

        if self.processor:
            self.processor.close()

        event.accept()


def run():

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )