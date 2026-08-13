"""Market Data Engine domain events.

Published on the existing :class:`~quant_os.events.EventBus`
(:class:`~quant_os.events.AsyncEventBus`). Tick events reuse
:class:`quant_os.events.MarketTickReceived` from Milestone 3 rather than
duplicating it — these are the additional lifecycle events specific to
the Market Data Engine.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field

from quant_os.events.base import Event
from quant_os.events.enums import EventType
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol


class QuoteUpdated(Event):
    """A new quote was received for a symbol.

    Attributes:
        quote: The updated quote.
    """

    event_type: EventType = EventType.QUOTE_UPDATED
    quote: Quote


class CandleOpened(Event):
    """A new candle period began for a symbol/timeframe.

    Attributes:
        symbol: The instrument the candle belongs to.
        timeframe: The bar granularity.
    """

    event_type: EventType = EventType.CANDLE_OPENED
    symbol: Symbol
    timeframe: str


class CandleClosed(Event):
    """A candle period completed for a symbol/timeframe.

    Attributes:
        candle: The completed candle.
    """

    event_type: EventType = EventType.CANDLE_CLOSED
    candle: OHLCVCandle


class MarketOpened(Event):
    """A market transitioned to open for trading.

    Attributes:
        symbol: The instrument whose market opened.
    """

    event_type: EventType = EventType.MARKET_OPENED
    symbol: Symbol


class MarketClosed(Event):
    """A market transitioned to closed for trading.

    Attributes:
        symbol: The instrument whose market closed.
    """

    event_type: EventType = EventType.MARKET_CLOSED
    symbol: Symbol


class ProviderConnected(Event):
    """A market data provider established a connection.

    Attributes:
        provider_name: The name of the provider that connected.
    """

    event_type: EventType = EventType.PROVIDER_CONNECTED
    provider_name: str


class ProviderDisconnected(Event):
    """A market data provider's connection was torn down.

    Attributes:
        provider_name: The name of the provider that disconnected.
        reason: A short description of why the disconnect occurred.
    """

    event_type: EventType = EventType.PROVIDER_DISCONNECTED
    provider_name: str
    reason: str = ""


class HistoricalDataLoaded(Event):
    """A historical data load completed for a symbol/timeframe.

    Attributes:
        symbol: The instrument the load was for.
        timeframe: The bar granularity that was loaded.
        candle_count: The number of candles loaded.
        request_id: An identifier correlating this event with the request
            that triggered the load.
    """

    event_type: EventType = EventType.HISTORICAL_DATA_LOADED
    symbol: Symbol
    timeframe: str
    candle_count: int
    request_id: UUID = Field(default_factory=uuid4)
