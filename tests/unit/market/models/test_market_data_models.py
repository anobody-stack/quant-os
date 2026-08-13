"""Unit tests for Tick, Quote, OHLCVCandle, and OrderBookSnapshot."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError as PydanticValidationError

from quant_os.core.exceptions import ValidationError
from quant_os.core.types import Price, Quantity
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.orderbook import OrderBookLevel, OrderBookSnapshot
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame

_XAU = Symbol(code="XAUUSD")
_NOW = datetime.now(UTC)
_NAIVE = datetime(2024, 1, 1)


class TestTick:
    def test_valid(self) -> None:
        tick = Tick(symbol=_XAU, price=Price(Decimal("1900")), timestamp=_NOW)
        assert tick.volume is None

    def test_naive_timestamp_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Tick(symbol=_XAU, price=Price(Decimal("1900")), timestamp=_NAIVE)

    def test_is_immutable(self) -> None:
        tick = Tick(symbol=_XAU, price=Price(Decimal("1900")), timestamp=_NOW)
        with pytest.raises(PydanticValidationError):
            tick.price = Price(Decimal("2000"))  # type: ignore[misc]


class TestQuote:
    def test_valid(self) -> None:
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
        )
        assert quote.bid.value < quote.ask.value

    def test_bid_equals_ask_allowed(self) -> None:
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900")), timestamp=_NOW
        )
        assert quote.bid.value == quote.ask.value

    def test_bid_greater_than_ask_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            Quote(
                symbol=_XAU,
                bid=Price(Decimal("1901")),
                ask=Price(Decimal("1900")),
                timestamp=_NOW,
            )

    def test_naive_timestamp_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Quote(
                symbol=_XAU,
                bid=Price(Decimal("1900")),
                ask=Price(Decimal("1901")),
                timestamp=_NAIVE,
            )


class TestOHLCVCandle:
    def _base_kwargs(self) -> dict[str, Any]:
        return {
            "symbol": _XAU,
            "timeframe": TimeFrame.M1,
            "open": Price(Decimal("1900")),
            "high": Price(Decimal("1905")),
            "low": Price(Decimal("1899")),
            "close": Price(Decimal("1902")),
            "volume": Quantity(Decimal("10")),
            "open_time": _NOW,
            "close_time": _NOW + timedelta(minutes=1),
        }

    def test_valid(self) -> None:
        candle = OHLCVCandle(**self._base_kwargs())
        assert candle.high.value >= candle.low.value

    def test_low_greater_than_high_rejected(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["low"] = Price(Decimal("1910"))
        with pytest.raises(PydanticValidationError):
            OHLCVCandle(**kwargs)

    def test_open_outside_range_rejected(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["open"] = Price(Decimal("2000"))
        with pytest.raises(PydanticValidationError):
            OHLCVCandle(**kwargs)

    def test_close_outside_range_rejected(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["close"] = Price(Decimal("1"))
        with pytest.raises(PydanticValidationError):
            OHLCVCandle(**kwargs)

    def test_close_time_before_open_time_rejected(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["close_time"] = _NOW - timedelta(minutes=1)
        with pytest.raises(PydanticValidationError):
            OHLCVCandle(**kwargs)

    def test_equal_open_high_low_close_allowed(self) -> None:
        kwargs = self._base_kwargs()
        for field_name in ("open", "high", "low", "close"):
            kwargs[field_name] = Price(Decimal("1900"))
        candle = OHLCVCandle(**kwargs)
        assert candle.open.value == candle.close.value


class TestOrderBookSnapshot:
    def test_valid(self) -> None:
        book = OrderBookSnapshot(
            symbol=_XAU,
            bids=(OrderBookLevel(price=Price(Decimal("1900")), quantity=Quantity(Decimal("5"))),),
            asks=(),
            timestamp=_NOW,
        )
        assert len(book.bids) == 1
        assert book.asks == ()

    def test_naive_timestamp_rejected(self) -> None:
        with pytest.raises(ValidationError):
            OrderBookSnapshot(symbol=_XAU, bids=(), asks=(), timestamp=_NAIVE)
