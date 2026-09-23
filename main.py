import os
import sys

if "--legacy-windows" in sys.argv:
    os.environ["MATH_EQUALIZER_LEGACY_WINDOWS"] = "1"

from math_equalizer.app import run


if __name__ == "__main__":
    run()
