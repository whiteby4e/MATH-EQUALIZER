import numpy as np

from math_equalizer.formula import SafeFormula
from math_equalizer.synth import synthesize_formula


def test_synth_generates_440_hz_sine_samples():
    sample_rate = 44100
    block = synthesize_formula(
        SafeFormula("sin(2*pi*440*t)"), 0, sample_rate, sample_rate
    )
    assert block.dtype == np.float32
    assert block.shape == (sample_rate,)
    assert np.max(block) <= 1.0
    assert np.min(block) >= -1.0
    zero_crossings = np.count_nonzero(np.diff(np.signbit(block)))
    assert 875 <= zero_crossings <= 885


def test_synth_formula_can_make_a_silence_block():
    block = synthesize_formula(SafeFormula("0"), 0, 256, 22050)
    assert np.all(block == 0)
