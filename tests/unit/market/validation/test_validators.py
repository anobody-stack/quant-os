"""Unit tests for market data validators."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Price
from quant_os.market.models.precision import PricePrecision
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.validation.validators import validate_precision, validate_quote, validate_tick

_XAU = Symbol(code="XAUUSD")


def _tick(price: str = "1900", when: datetime | None = None) -> Tick:
    return Tick(symbol=_XAU, price=Price(Decimal(price)), timestamp=when or datetime.now(UTC))


class TestValidateTick:
    def test_valid_tick_passes(self) -> None:
        tick = _tick()
        assert validate_tick(tick) is tick

    def test_future_timestamp_rejected(self) -> None:
        future = datetime.now(UTC) + timedelta(hours=1)
        with pytest.raises(ValidationError):
            validate_tick(_tick(when=future))

    def test_duplicate_tick_rejected(self) -> None:
        when = datetime.now(UTC)
        last = _tick(price="1900", when=when)
        new = _tick(price="1900", when=when)
        with pytest.raises(ValidationError):
            validate_tick(new, last_tick=last)

    def test_different_price_same_timestamp_allowed(self) -> None:
        when = datetime.now(UTC)
        last = _tick(price="1900", when=when)
        new = _tick(price="1901", when=when)
        assert validate_tick(new, last_tick=last) is new

    def test_no_last_tick_allowed(self) -> None:
        tick = _tick()
        assert validate_tick(tick, last_tick=None) is tick


class TestValidateQuote:
    def test_valid_quote_passes(self) -> None:
        quote = Quote(
            symbol=_XAU,
            bid=Price(Decimal("1900")),
            ask=Price(Decimal("1900.5")),
            timestamp=datetime.now(UTC),
        )
        assert validate_quote(quote) is quote

    def test_future_timestamp_rejected(self) -> None:
        future = datetime.now(UTC) + timedelta(hours=1)
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=future
        )
        with pytest.raises(ValidationError):
            validate_quote(quote)


class TestValidatePrecision:
    def test_matching_precision_passes(self) -> None:
        precision = PricePrecision(decimal_places=2, tick_size=Decimal("0.01"))
        price = Price(Decimal("1900.50"))
        assert validate_precision(price, precision) is price

    def test_non_conforming_precision_rejected(self) -> None:
        precision = PricePrecision(decimal_places=2, tick_size=Decimal("0.01"))
        price = Price(Decimal("1900.505"))
        with pytest.raises(ValidationError):
            validate_precision(price, precision)
