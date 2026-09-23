"""Qt compatibility layer for modern and legacy Windows builds."""

from __future__ import annotations
import os
import sys

LEGACY_WINDOWS = os.environ.get("MATH_EQUALIZER_LEGACY_WINDOWS") == "1" or "--legacy-windows" in sys.argv

if LEGACY_WINDOWS:
    from PySide2.QtCore import QTimer, Qt
    from PySide2.QtWidgets import QApplication, QFileDialog, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
else:
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtWidgets import QApplication, QFileDialog, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget


def exec_app(app):
    return app.exec_() if LEGACY_WINDOWS else app.exec()
