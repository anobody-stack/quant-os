"""Unit tests for the Quantity value type."""

from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Quantity


def test_valid_quantity() -> None:
    assert Quantity(Decimal("10")).value == Decimal("10")


def test_zero_quantity_allowed() -> None:
    assert Quantity(Decimal("0")).value == Decimal("0")


def test_negative_quantity_raises() -> None:
    with pytest.raises(ValidationError):
        Quantity(Decimal("-1"))


def test_invalid_type_raises() -> None:
    with pytest.raises(ValidationError):
        Quantity("not-a-decimal")  # type: ignore[arg-type]


def test_is_immutable() -> None:
    quantity = Quantity(Decimal("10"))
    with pytest.raises(AttributeError):
        quantity.value = Decimal("20")  # type: ignore[misc]


def test_str_representation() -> None:
    assert str(Quantity(Decimal("10"))) == "10"
