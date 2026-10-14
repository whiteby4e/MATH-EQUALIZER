# MATH-EQUALIZER

A mathematical audio processor that transforms music with formulas and mathematical functions.

## Features

- Load WAV, AIFF, FLAC, and OGG audio and apply formulas to BASS, MID, TREBLE, or FULL spectrum.
- **Generate sound directly from a formula**, without loading an audio file.
- Compact calculator-style formula editor with shortcut keys for common math functions.
- Safe, restricted AST-based formula evaluator.
- Real-time playback controls and optional formula/FFT visualization.
- Low Power mode for older or weaker computers.
- Separate modern and legacy Windows GUI paths.

## Generate sound from a formula

Switch **Mode** to **Generate sound from formula**, enter an expression, and press **Generate / Play**.

The variable \`t\` is time in seconds. For example:

\`\`\`text
sin(2*pi*440*t)
\`\`\`

This generates a 440 Hz sine wave. Other examples:

| Formula | Result |
|---|---|
| \`sin(2*pi*220*t)\` | Lower-pitched sine wave |
| \`0.5*sin(2*pi*440*t) + 0.25*sin(2*pi*660*t)\` | Two-tone blend |
| \`sin(2*pi*(220+80*sin(2*pi*2*t))*t)\` | Wobbling, synthesizer-like tone |
| \`0\` | Silence |

Output is clipped to the range -1 to 1. Playback is limited to 30 seconds per pass and can be restarted. The Low Power build uses 22.05 kHz synthesis; the normal build uses 44.1 kHz.

Supported constants and functions:

\`\`\`text
pi, e, sin, cos, tan, exp, sqrt, abs, log, log10, floor, ceil
\`\`\`

Use multiplication explicitly: \`2*pi*440*t\`. The formula evaluator does not use Python's \`eval\` environment directly; it validates a restricted expression tree before evaluation.

## Process an audio file

Switch **Mode** to **Process an audio file**, choose a supported audio file, enter a gain formula, select the frequency band, and press Play.

Example:

\`\`\`text
1 + 0.5*sin(2*pi*2*t)
\`\`\`

This varies the gain over time. Frequency bands:

| Band | Frequency range |
|---|---|
| BASS | Below 250 Hz |
| MID | 250 Hz – 4 kHz |
| TREBLE | 4 kHz and above |
| FULL | Entire spectrum |

## Low Power Mode

Low Power mode reduces work on older computers by disabling live graphs, avoiding Matplotlib, using a smaller FFT and larger processing hop for file processing, reducing the synthesis sample rate, and refreshing the interface less often. It preserves the main playback and formula features. Results depend on the computer and audio device.

Run manually:

\`\`\`bash
python main.py --low-power
\`\`\`

For legacy Windows:

\`\`\`bat
python main.py --legacy-windows --low-power
\`\`\`

## Windows compatibility

| Windows | GUI stack | Python |
|---|---|---|
| Windows 10/11 current builds | Modern: PySide6 / Qt 6 | Python 3.10+ |
| Windows 10 old builds, including 15063 (1703) | Legacy: PySide2 / Qt 5 | Python 3.8.x |
| Windows 8.1 | Legacy: PySide2 / Qt 5 | Python 3.8.x |
| Windows 7 SP1 | Legacy: PySide2 / Qt 5 | Python 3.8.x |

Use the matching launcher:

- Windows 7: \`math_equalizer/run_windows_7.bat\`
- Windows 8.1: \`math_equalizer/run_windows_8_1.bat\`
- Windows 10 old builds: \`math_equalizer/run_windows_10_legacy.bat\`
- Current Windows 10/11: \`math_equalizer/run_windows_10_11.bat\`
- Windows Low Power: \`math_equalizer/run_windows_low_power.bat\`
- Legacy Windows Low Power: \`math_equalizer/run_windows_legacy_low_power.bat\`

Modern and legacy environments are separated to prevent Qt dependency conflicts.

## Other platforms

- Linux: \`math_equalizer/run_linux.sh\` or \`math_equalizer/run_linux_low_power.sh\`
- macOS: \`math_equalizer/run_macos.sh\` or \`math_equalizer/run_macos_low_power.sh\`

## Installation

\`\`\`bash
git clone https://github.com/whiteby4e/MATH-EQUALIZER.git
cd MATH-EQUALIZER
python -m venv .venv
python -m pip install -r requirements.txt
python main.py
\`\`\`

Use \`requirements-legacy-windows.txt\` and Python 3.8.x for the legacy Windows path. The project uses NumPy, sounddevice, soundfile, and PySide; Matplotlib is only needed for the normal visualization mode.

## Tests

\`\`\`bash
python -m pytest
\`\`\`

## License

MIT License. See [LICENSE](LICENSE).
