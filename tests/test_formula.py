import numpy as np
import pytest

from math_equalizer.formula import FormulaError, SafeFormula


def test_formula_vectorizes():
    value = SafeFormula("1 + 0.5*sin(2*pi*t)").evaluate(np.array([0.0, 0.25]))
    assert value.shape == (2,)
    assert np.all(np.isfinite(value))


def test_unknown_names_are_rejected():
    with pytest.raises(FormulaError):
        SafeFormula("__import__('os')")


def test_large_powers_are_rejected():
    with pytest.raises(FormulaError):
        SafeFormula("t**1000000")
