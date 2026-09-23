# MATH-EQUALIZER

A mathematical audio processor that transforms and manipulates music using formulas and mathematical functions.

MATH-EQUALIZER lets you load an audio file, apply a time-based mathematical formula to a selected frequency range, and hear the result in real time.

## Features

- 🎵 Load WAV, AIFF, FLAC, and OGG audio
- 🧮 Control audio gain with mathematical formulas
- 🎚️ Apply formulas to BASS, MID, TREBLE, or FULL spectrum
- 📈 Real-time formula and FFT visualization
- ▶️ Play, pause, and stop controls
- 🔒 Formula expressions are validated with a restricted AST-based evaluator
- 🪶 Low Power Mode for older or weaker computers
- 🪟 Windows launch scripts included

## How the formula works

The variable `t` represents time in seconds.

Example:

```text
1 + 0.5*sin(2*pi*2*t)
```

This creates a gain value that changes over time.

Available constants and functions include:

```text
pi
e
sin
cos
tan
exp
sqrt
abs
log
log10
floor
ceil
```

The final gain is limited by the audio processor to keep the output in a safe numerical range.

## Frequency bands

| Band | Frequency range |
|---|---|
| BASS | Below 250 Hz |
| MID | 250 Hz – 4 kHz |
| TREBLE | 4 kHz and above |
| FULL | Entire spectrum |

## Requirements

- Python 3.10 or newer
- Windows, Linux, or macOS
- A working audio output device

## Installation

Clone the repository:

```bash
git clone https://github.com/whiteby4e/MATH-EQUALIZER.git
cd MATH-EQUALIZER
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\\Scripts\\activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Windows

For normal mode, run:

```text
math_equalizer/run_windows.bat
```

The script creates the virtual environment if needed, installs dependencies, and starts the application.

## Low Power Mode

Older computers can use **Low Power Mode** to reduce CPU and RAM usage.

Low Power Mode:

- disables the live graphs
- avoids loading Matplotlib
- uses a smaller FFT size
- uses a larger processing hop
- updates the lightweight interface less often
- keeps the main audio-processing functionality

### Windows

Run:

```text
math_equalizer/run_windows_low_power.bat
```

Or start it manually:

```bash
python main.py --low-power
```

The low-power launcher uses `requirements-lite.txt`, which does not install Matplotlib.

### When to use it

Use Low Power Mode if the normal version causes:

- high CPU usage
- audio dropouts
- slow interface response
- excessive memory usage

The normal mode is intended for computers that can comfortably handle real-time FFT visualization.

## Project structure

```text
MATH-EQUALIZER/
├── main.py
├── requirements.txt
├── requirements-lite.txt
├── LICENSE
├── README.md
└── math_equalizer/
    ├── __init__.py
    ├── app.py
    ├── audio.py
    ├── formula.py
    ├── visualizer.py
    ├── run_windows.bat
    └── run_windows_low_power.bat
```

## Notes

- This project changes audio using mathematical gain functions; it is an experimental audio-processing project rather than a conventional graphic equalizer.
- Formula values are evaluated over time and applied to the selected frequency band.
- Very large or rapidly changing formulas can still require more CPU.
- Low Power Mode removes visualization overhead but does not guarantee real-time playback on every old computer.
- The project currently focuses on local audio-file playback.

## License

MIT License. See [LICENSE](LICENSE).
