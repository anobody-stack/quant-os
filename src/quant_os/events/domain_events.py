"""Concrete domain event definitions.

Each class here is a pure data model describing the shape of a specific
event. None of them contain business logic — classification, scoring,
and any other domain behavior are the responsibility of later milestones.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from quant_os.core.types import Confidence, Money, Price, Quantity
from quant_os.events.base import Event
from quant_os.events.enums import EventPriority, EventType


class NewsReceived(Event):
    """A news article was received from a provider.

    Attributes:
        article_id: Unique identifier for the article.
        title: The article headline.
        source_name: Name of the originating news source.
        published_at: UTC time the article was published by its source.
    """

    event_type: EventType = EventType.NEWS_RECEIVED
    article_id: UUID = Field(default_factory=uuid4)
    title: str
    source_name: str
    published_at: datetime


class EconomicEventReceived(Event):
    """An economic calendar event was received from a provider.

    Attributes:
        economic_event_id: Unique identifier for the calendar event.
        name: Name of the event (e.g. "Non-Farm Payrolls").
        country: Standardized country identifier the event pertains to.
        scheduled_at: UTC time the event is scheduled to occur.
    """

    event_type: EventType = EventType.ECONOMIC_EVENT_RECEIVED
    economic_event_id: UUID = Field(default_factory=uuid4)
    name: str
    country: str
    scheduled_at: datetime


class MarketTickReceived(Event):
    """A market data tick was received from a provider.

    Attributes:
        symbol: The instrument symbol the tick pertains to.
        price: The traded or quoted price.
        quantity: The traded size, if applicable to this tick.
        tick_time: UTC time the tick occurred.
    """

    event_type: EventType = EventType.MARKET_TICK_RECEIVED
    symbol: str
    price: Price
    quantity: Quantity | None = None
    tick_time: datetime


class SignalGenerated(Event):
    """A strategy or agent generated a trading signal.

    Attributes:
        signal_id: Unique identifier for the signal.
        symbol: The instrument symbol the signal pertains to.
        direction: The signal's direction (e.g. "long", "short", "flat").
        confidence: The signal generator's confidence in this signal.
    """

    event_type: EventType = EventType.SIGNAL_GENERATED
    signal_id: UUID = Field(default_factory=uuid4)
    symbol: str
    direction: str
    confidence: Confidence


class RiskAlert(Event):
    """A risk condition was detected.

    Attributes:
        alert_id: Unique identifier for the alert.
        message: Human-readable description of the risk condition.
        severity: How urgent the alert is.
    """

    event_type: EventType = EventType.RISK_ALERT
    alert_id: UUID = Field(default_factory=uuid4)
    message: str
    severity: EventPriority


class OrderCreated(Event):
    """An order was created.

    Attributes:
        order_id: Unique identifier for the order.
        symbol: The instrument symbol being ordered.
        quantity: The order quantity.
        limit_price: The limit price, if this is a limit order.
    """

    event_type: EventType = EventType.ORDER_CREATED
    order_id: UUID = Field(default_factory=uuid4)
    symbol: str
    quantity: Quantity
    limit_price: Price | None = None


class OrderFilled(Event):
    """An order was filled, in whole or in part.

    Attributes:
        order_id: Unique identifier for the order that was filled.
        fill_price: The price at which the fill occurred.
        fill_quantity: The quantity that was filled.
    """

    event_type: EventType = EventType.ORDER_FILLED
    order_id: UUID
    fill_price: Price
    fill_quantity: Quantity


class PositionOpened(Event):
    """A new position was opened.

    Attributes:
        position_id: Unique identifier for the position.
        symbol: The instrument symbol.
        quantity: The position size.
        entry_price: The average entry price.
    """

    event_type: EventType = EventType.POSITION_OPENED
    position_id: UUID = Field(default_factory=uuid4)
    symbol: str
    quantity: Quantity
    entry_price: Price


class PositionClosed(Event):
    """An existing position was closed.

    Attributes:
        position_id: Unique identifier for the position that was closed.
        exit_price: The average exit price.
        realized_pnl: The realized profit or loss from the position.
    """

    event_type: EventType = EventType.POSITION_CLOSED
    position_id: UUID
    exit_price: Price
    realized_pnl: Money


class PortfolioUpdated(Event):
    """A portfolio's aggregate state changed.

    Attributes:
        portfolio_id: Unique identifier for the portfolio.
        total_value: The portfolio's total value as of ``as_of``.
        as_of: UTC time the valuation was computed.
    """

    event_type: EventType = EventType.PORTFOLIO_UPDATED
    portfolio_id: UUID = Field(default_factory=uuid4)
    total_value: Money
    as_of: datetime
