@echo off
title Math Equalizer - Legacy Windows

if not exist .venv-legacy (
    py -3.8 -m venv .venv-legacy
)

call .venv-legacy\Scripts\activate.bat
python -m pip install --upgrade "pip<24.1"
python -m pip install -r requirements-legacy-windows.txt
python main.py --legacy-windows
pause
