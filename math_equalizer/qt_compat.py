"""Qt compatibility layer for modern and legacy Windows builds."""

from __future__ import annotations

import sys

# A packaged legacy build contains PySide2, while a modern build contains
# PySide6. Prefer PySide2 when it is available so the same source works from
# both source checkouts and frozen executables.
try:
    from PySide2.QtCore import QTimer, Qt
    from PySide2.QtWidgets import (
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
        QWidget,
    )
    LEGACY_WINDOWS = True
except ImportError:
    from PySide6.QtCore import QTimer, Qt
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
        QWidget,
    )
    LEGACY_WINDOWS = False


def exec_app(app):
    return app.exec_() if LEGACY_WINDOWS else app.exec()
