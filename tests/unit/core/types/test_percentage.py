"""Unit tests for the Percentage value type."""

from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Percentage


def test_valid_percentage() -> None:
    assert Percentage(Decimal("50")).value == Decimal("50")


def test_boundary_values_allowed() -> None:
    assert Percentage(Decimal("0")).value == Decimal("0")
    assert Percentage(Decimal("100")).value == Decimal("100")


def test_below_zero_raises() -> None:
    with pytest.raises(ValidationError):
        Percentage(Decimal("-1"))


def test_above_hundred_raises() -> None:
    with pytest.raises(ValidationError):
        Percentage(Decimal("101"))


def test_as_fraction() -> None:
    assert Percentage(Decimal("25")).as_fraction() == Decimal("0.25")


def test_is_immutable() -> None:
    pct = Percentage(Decimal("50"))
    with pytest.raises(AttributeError):
        pct.value = Decimal("60")  # type: ignore[misc]


def test_str_representation() -> None:
    assert str(Percentage(Decimal("12.5"))) == "12.5%"
