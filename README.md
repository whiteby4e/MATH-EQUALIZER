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

## Windows compatibility

MATH-EQUALIZER now has two Windows GUI paths:

| Windows | Build | GUI stack |
|---|---|---|
| Windows 10/11 | Modern | PySide6 / Qt 6 |
| Windows 10 old builds, including 15063 (1703) | Legacy | PySide2 / Qt 5 |
| Windows 8.1 | Legacy | PySide2 / Qt 5 |
| Windows 7 SP1 | Legacy | PySide2 / Qt 5 |

The legacy path is separate from the modern dependencies because current Qt 6/PySide6 releases do not target Windows 7/8.1 and require newer Windows 10 builds.

For legacy Windows, use Python 3.8.x and the dedicated launcher.

### Legacy Windows

Run: `math_equalizer/run_windows_legacy.bat`

For older or weaker legacy PCs, use: `math_equalizer/run_windows_legacy_low_power.bat`

Manual commands:

`python main.py --legacy-windows`

`python main.py --legacy-windows --low-power`

The legacy and modern launchers use separate virtual environments (`.venv-legacy` and `.venv`) so their Qt versions do not conflict.
## Platform launch links

Use the launcher that matches your operating system:

### Windows

| Windows version | Launcher |
|---|---|
| Windows 7 SP1 | [Windows 7 launcher](math_equalizer/run_windows_7.bat) |
| Windows 8.1 | [Windows 8.1 launcher](math_equalizer/run_windows_8_1.bat) |
| Windows 10 old builds, including 15063 (1703) | [Windows 10 Legacy launcher](math_equalizer/run_windows_10_legacy.bat) |
| Windows 10/11 current builds | [Windows 10/11 launcher](math_equalizer/run_windows_10_11.bat) |

Legacy Windows uses Python 3.8.x and the PySide2/Qt 5 compatibility path.

### Linux

- [Linux normal launcher](math_equalizer/run_linux.sh)
- [Linux Low Power launcher](math_equalizer/run_linux_low_power.sh)

### macOS

- [macOS normal launcher](math_equalizer/run_macos.sh)
- [macOS Low Power launcher](math_equalizer/run_macos_low_power.sh)

The Linux and macOS launchers use the modern Python/PySide6 dependency set. Run shell launchers with "bash" if the executable bit is not preserved by your download method.

## Downloads

Prebuilt packages are published as GitHub Releases:

| Platform | Download |
|---|---|
| Windows 10/11 (modern) | [Windows Modern](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-windows-modern.zip) |
| Windows 10 old builds / 8.1 / 7 SP1 | [Windows Legacy](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-windows-legacy.zip) |
| Linux x64 | [Linux x64](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-linux-x64.zip) |
| macOS Apple Silicon | [macOS Apple Silicon](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-macos-arm64.zip) |

These links point to the latest release. Packages are generated automatically when a version tag such as `v0.1.0` is pushed.
## Requirements

- Python 3.10 or newer for the modern build
- Python 3.8.x for the legacy Windows build
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
