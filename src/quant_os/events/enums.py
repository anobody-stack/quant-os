"""Event classification enumerations.

These enums are the vocabulary the event system is built on. `EventType`
identifies what kind of thing happened; `EventPriority` identifies how
urgently it should be handled. Both are deliberately generic — neither
encodes any business or trading logic.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum


class EventType(StrEnum):
    """The kind of domain event being published on the event bus."""

    NEWS_RECEIVED = "news_received"
    ECONOMIC_EVENT_RECEIVED = "economic_event_received"
    MARKET_TICK_RECEIVED = "market_tick_received"
    SIGNAL_GENERATED = "signal_generated"
    RISK_ALERT = "risk_alert"
    ORDER_CREATED = "order_created"
    ORDER_FILLED = "order_filled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    PORTFOLIO_UPDATED = "portfolio_updated"

    # Market Data Engine (Milestone 5)
    QUOTE_UPDATED = "quote_updated"
    CANDLE_OPENED = "candle_opened"
    CANDLE_CLOSED = "candle_closed"
    MARKET_OPENED = "market_opened"
    MARKET_CLOSED = "market_closed"
    PROVIDER_CONNECTED = "provider_connected"
    PROVIDER_DISCONNECTED = "provider_disconnected"
    HISTORICAL_DATA_LOADED = "historical_data_loaded"


class EventPriority(IntEnum):
    """The urgency of an event, ordered from least to most urgent.

    Modeled as an ``IntEnum`` (rather than a string enum) so that
    priorities can be compared and sorted directly, e.g. for a future
    priority-aware dispatch strategy.
    """

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3
