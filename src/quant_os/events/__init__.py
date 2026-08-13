"""QuantOS event system.

This is core infrastructure: every future subsystem (market data, news,
strategy agents, risk, portfolio, execution, AI, reporting) communicates
through the :class:`~quant_os.events.bus.EventBus` using the domain events
defined in :mod:`quant_os.events.domain_events`.

This package contains no business logic — only the event envelope,
concrete event data models, and the publish/subscribe abstraction itself.
"""

from quant_os.events.async_bus import AsyncEventBus
from quant_os.events.base import Event
from quant_os.events.bus import EventBus, EventHandler, Middleware, SubscriptionId
from quant_os.events.domain_events import (
    EconomicEventReceived,
    MarketTickReceived,
    NewsReceived,
    OrderCreated,
    OrderFilled,
    PortfolioUpdated,
    PositionClosed,
    PositionOpened,
    RiskAlert,
    SignalGenerated,
)
from quant_os.events.enums import EventPriority, EventType
from quant_os.events.metadata import EventMetadata

__all__ = [
    "AsyncEventBus",
    "EconomicEventReceived",
    "Event",
    "EventBus",
    "EventHandler",
    "EventMetadata",
    "EventPriority",
    "EventType",
    "MarketTickReceived",
    "Middleware",
    "NewsReceived",
    "OrderCreated",
    "OrderFilled",
    "PortfolioUpdated",
    "PositionClosed",
    "PositionOpened",
    "RiskAlert",
    "SignalGenerated",
    "SubscriptionId",
]
