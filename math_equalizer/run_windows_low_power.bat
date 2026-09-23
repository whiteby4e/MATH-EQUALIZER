@echo off
title Math Equalizer - Low Power Mode

if not exist .venv (
    py -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements-lite.txt

python main.py --low-power

pause
