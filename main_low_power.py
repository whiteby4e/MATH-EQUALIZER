"""Low-power packaged entry point for MATH-EQUALIZER."""

import sys

if "--low-power" not in sys.argv:
    sys.argv.append("--low-power")

from math_equalizer.app import run


if __name__ == "__main__":
    run()
