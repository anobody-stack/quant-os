"""Unit tests for the Confidence value type."""

from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Confidence, Probability


def test_valid_confidence() -> None:
    assert Confidence(Decimal("0.9")).value == Decimal("0.9")


def test_boundary_values_allowed() -> None:
    assert Confidence(Decimal("0")).value == Decimal("0")
    assert Confidence(Decimal("1")).value == Decimal("1")


def test_below_zero_raises() -> None:
    with pytest.raises(ValidationError):
        Confidence(Decimal("-0.1"))


def test_above_one_raises() -> None:
    with pytest.raises(ValidationError):
        Confidence(Decimal("1.1"))


def test_is_immutable() -> None:
    confidence = Confidence(Decimal("0.5"))
    with pytest.raises(AttributeError):
        confidence.value = Decimal("0.9")  # type: ignore[misc]


def test_str_representation() -> None:
    assert str(Confidence(Decimal("0.9"))) == "0.9"


def test_is_distinct_type_from_probability() -> None:
    """Confidence and Probability are intentionally distinct, non-interchangeable types."""
    assert Confidence is not Probability
