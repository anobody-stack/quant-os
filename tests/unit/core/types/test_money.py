"""Unit tests for the Money value type."""

from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Money


def test_valid_money() -> None:
    money = Money(Decimal("100.50"), "USD")
    assert money.amount == Decimal("100.50")
    assert money.currency == "USD"


def test_negative_amount_allowed() -> None:
    """Negative amounts are structurally valid (e.g. debits); no business rule forbids it."""
    money = Money(Decimal("-50"), "USD")
    assert money.amount == Decimal("-50")


def test_invalid_currency_length_raises() -> None:
    with pytest.raises(ValidationError):
        Money(Decimal("10"), "US")


def test_invalid_currency_case_raises() -> None:
    with pytest.raises(ValidationError):
        Money(Decimal("10"), "usd")


def test_invalid_amount_type_raises() -> None:
    with pytest.raises(ValidationError):
        Money("not-a-decimal", "USD")  # type: ignore[arg-type]


def test_is_immutable() -> None:
    money = Money(Decimal("10"), "USD")
    with pytest.raises(AttributeError):
        money.amount = Decimal("20")  # type: ignore[misc]


def test_str_representation() -> None:
    money = Money(Decimal("100.50"), "USD")
    assert str(money) == "100.50 USD"
