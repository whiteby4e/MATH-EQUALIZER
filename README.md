<div align="center">

# MATH-EQUALIZER

**Shape sound with mathematics.**

An experimental audio processor that applies time-dependent mathematical gain functions to selected frequency bands — with live playback and visual feedback.

[Features](#-features) · [Quick start](#-quick-start) · [Formula guide](#-formula-guide) · [Downloads](#-downloads) · [Compatibility](#-compatibility)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational)

</div>

---

## 🎛️ What is it?

MATH-EQUALIZER lets you load an audio file, choose a frequency band, and control its gain with a mathematical expression that changes over time. Instead of drawing a conventional EQ curve, you describe how the gain should behave.

It is an experimental **math-driven audio processor**, not a traditional graphic equalizer.

## ✨ Features

- Load WAV, AIFF, FLAC, and OGG audio.
- Apply formulas to **BASS**, **MID**, **TREBLE**, or the **FULL** spectrum.
- View live formula and FFT visualizations.
- Play, pause, and stop audio.
- Evaluate expressions with a restricted AST-based evaluator.
- Use Low Power Mode on older or resource-limited computers.
- Run on modern Windows, older Windows releases, Linux, and macOS (see compatibility notes).

## ⚡ Quick start

### Download a ready-to-run build

Get the latest package from [GitHub Releases](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest).

| Platform | Package |
|---|---|
| Windows 10/11 (modern) | [Download](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-windows-modern.zip) |
| Windows 7 / 8.1 / older Windows 10 | [Download legacy build](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-windows-legacy.zip) |
| Linux x64 | [Download](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-linux-x64.zip) |
| macOS Apple Silicon | [Download](https://github.com/whiteby4e/MATH-EQUALIZER/releases/latest/download/math-equalizer-macos-arm64.zip) |

macOS Intel packages are not currently available.

### Run from source

```bash
git clone https://github.com/whiteby4e/MATH-EQUALIZER.git
cd MATH-EQUALIZER
python -m venv .venv
```

Activate the environment, then install and run:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
python main.py
```

For the modern build, use Python 3.10 or newer.

## 🧮 Formula guide

The variable `t` represents elapsed time in seconds.

Try this example:

```text
1 + 0.5*sin(2*pi*2*t)
```

It creates a gain value that oscillates over time. Available constants and functions include:

```text
pi, e
sin, cos, tan
exp, sqrt, abs
log, log10
floor, ceil
```

The processor limits the final gain to a safe numerical range. Very complex or rapidly changing expressions may still increase CPU usage.

## 🎚️ Frequency bands

| Band | Range |
|---|---:|
| BASS | Below 250 Hz |
| MID | 250 Hz – 4 kHz |
| TREBLE | Above 4 kHz |
| FULL | Entire spectrum |

## 🪶 Low Power Mode

Low Power Mode reduces visualization and processing overhead:

- Disables live graphs.
- Avoids loading Matplotlib.
- Uses a smaller FFT size and a larger processing hop.
- Updates the lightweight interface less often.

Run it with:

```bash
python main.py --low-power
```

On Windows, the included `run_windows_low_power.bat` launcher can also be used. Low Power Mode helps older computers, but cannot guarantee uninterrupted real-time playback on every system.

## 🪟 Compatibility

| Environment | GUI stack | Python |
|---|---|---|
| Windows 10/11 (modern builds) | PySide6 / Qt 6 | 3.10+ |
| Windows 10 build 15063 (1703), Windows 8.1, Windows 7 SP1 | PySide2 / Qt 5 | 3.8.x |
| Linux / macOS | PySide6 / Qt 6 | 3.10+ |

The legacy Windows path is kept separate from modern dependencies because current Qt 6 releases do not support Windows 7/8.1 and require newer Windows 10 builds.

## 🎹 MathRoll Easter egg

Enter `rickastly` in the formula field, choose **Apply Formula**, then press **Play** to discover a short original retro-pop synth sequence generated locally with mathematical oscillators. It does not require an audio file or an internet connection.

This is an unofficial fan-made tribute and is not affiliated with or endorsed by Rick Astley.

## 🧱 Project structure

```text
MATH-EQUALIZER/
├── main.py
├── requirements.txt
├── requirements-lite.txt
├── requirements-legacy-windows.txt
├── tests/
└── math_equalizer/
    ├── app.py
    ├── audio.py
    ├── formula.py
    ├── visualizer.py
    └── run_*.bat / run_*.sh
```

## 🧪 Tests

Run the formula evaluator tests with:

```bash
python -m unittest discover -s tests
```

## 📦 Releases

Versioned packages are built through the repository's GitHub Actions release workflow when a version tag (for example, `v0.1.0`) is pushed. See [all releases](https://github.com/whiteby4e/MATH-EQUALIZER/releases).

## 📄 License

MIT — see [LICENSE](LICENSE).
