"""Unit tests for the Probability value type."""

from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Probability


def test_valid_probability() -> None:
    assert Probability(Decimal("0.5")).value == Decimal("0.5")


def test_boundary_values_allowed() -> None:
    assert Probability(Decimal("0")).value == Decimal("0")
    assert Probability(Decimal("1")).value == Decimal("1")


def test_below_zero_raises() -> None:
    with pytest.raises(ValidationError):
        Probability(Decimal("-0.1"))


def test_above_one_raises() -> None:
    with pytest.raises(ValidationError):
        Probability(Decimal("1.1"))


def test_is_immutable() -> None:
    prob = Probability(Decimal("0.5"))
    with pytest.raises(AttributeError):
        prob.value = Decimal("0.9")  # type: ignore[misc]


def test_str_representation() -> None:
    assert str(Probability(Decimal("0.75"))) == "0.75"
