"""Unit tests for the Price value type."""

from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Price


def test_valid_price() -> None:
    assert Price(Decimal("1900.50")).value == Decimal("1900.50")


def test_zero_price_allowed() -> None:
    assert Price(Decimal("0")).value == Decimal("0")


def test_negative_price_raises() -> None:
    with pytest.raises(ValidationError):
        Price(Decimal("-1"))


def test_invalid_type_raises() -> None:
    with pytest.raises(ValidationError):
        Price("not-a-decimal")  # type: ignore[arg-type]


def test_is_immutable() -> None:
    price = Price(Decimal("10"))
    with pytest.raises(AttributeError):
        price.value = Decimal("20")  # type: ignore[misc]


def test_str_representation() -> None:
    assert str(Price(Decimal("1900.50"))) == "1900.50"
