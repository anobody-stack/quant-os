"""Unit tests for market-specific domain events."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from quant_os.core.types import Price, Quantity
from quant_os.events import EventMetadata
from quant_os.events.enums import EventType
from quant_os.market.events.market_events import (
    CandleClosed,
    CandleOpened,
    HistoricalDataLoaded,
    MarketClosed,
    MarketOpened,
    ProviderConnected,
    ProviderDisconnected,
    QuoteUpdated,
)
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.timeframe import TimeFrame

_XAU = Symbol(code="XAUUSD")
_NOW = datetime.now(UTC)
_METADATA = EventMetadata(source="test")


def test_quote_updated() -> None:
    quote = Quote(
        symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
    )
    event = QuoteUpdated(metadata=_METADATA, quote=quote)
    assert event.event_type == EventType.QUOTE_UPDATED


def test_candle_opened() -> None:
    event = CandleOpened(metadata=_METADATA, symbol=_XAU, timeframe=TimeFrame.M1.value)
    assert event.event_type == EventType.CANDLE_OPENED


def test_candle_closed() -> None:
    candle = OHLCVCandle(
        symbol=_XAU,
        timeframe=TimeFrame.M1,
        open=Price(Decimal("1900")),
        high=Price(Decimal("1901")),
        low=Price(Decimal("1899")),
        close=Price(Decimal("1900.5")),
        volume=Quantity(Decimal("10")),
        open_time=_NOW,
        close_time=_NOW + timedelta(minutes=1),
    )
    event = CandleClosed(metadata=_METADATA, candle=candle)
    assert event.event_type == EventType.CANDLE_CLOSED


def test_market_opened() -> None:
    event = MarketOpened(metadata=_METADATA, symbol=_XAU)
    assert event.event_type == EventType.MARKET_OPENED


def test_market_closed() -> None:
    event = MarketClosed(metadata=_METADATA, symbol=_XAU)
    assert event.event_type == EventType.MARKET_CLOSED


def test_provider_connected() -> None:
    event = ProviderConnected(metadata=_METADATA, provider_name="mock")
    assert event.event_type == EventType.PROVIDER_CONNECTED


def test_provider_disconnected() -> None:
    event = ProviderDisconnected(metadata=_METADATA, provider_name="mock", reason="shutdown")
    assert event.event_type == EventType.PROVIDER_DISCONNECTED
    assert event.reason == "shutdown"


def test_provider_disconnected_default_reason() -> None:
    event = ProviderDisconnected(metadata=_METADATA, provider_name="mock")
    assert event.reason == ""


def test_historical_data_loaded() -> None:
    event = HistoricalDataLoaded(
        metadata=_METADATA, symbol=_XAU, timeframe=TimeFrame.M1.value, candle_count=100
    )
    assert event.event_type == EventType.HISTORICAL_DATA_LOADED
    assert event.candle_count == 100
