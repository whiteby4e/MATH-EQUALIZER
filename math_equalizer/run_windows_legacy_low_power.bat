@echo off
title Math Equalizer - Legacy Windows Low Power Mode

if not exist .venv-legacy (
    py -3.8 -m venv .venv-legacy
)

call .venv-legacy\Scripts\activate.bat
python -m pip install --upgrade "pip<24.1"
python -m pip install numpy==1.24.4 sounddevice==0.4.6 soundfile==0.12.1 PySide2==5.15.2.1
python main.py --legacy-windows --low-power
pause
