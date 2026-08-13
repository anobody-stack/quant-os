"""Unit tests for concrete domain event models."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from quant_os.core.types import Confidence, Money, Price, Quantity
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

_METADATA = EventMetadata(source="test")


def test_news_received() -> None:
    event = NewsReceived(
        metadata=_METADATA,
        title="Fed holds rates steady",
        source_name="Reuters",
        published_at=datetime.now(UTC),
    )
    assert event.event_type == EventType.NEWS_RECEIVED


def test_economic_event_received() -> None:
    event = EconomicEventReceived(
        metadata=_METADATA,
        name="Non-Farm Payrolls",
        country="United States",
        scheduled_at=datetime.now(UTC),
    )
    assert event.event_type == EventType.ECONOMIC_EVENT_RECEIVED


def test_market_tick_received() -> None:
    event = MarketTickReceived(
        metadata=_METADATA,
        symbol="XAUUSD",
        price=Price(Decimal("1900.50")),
        quantity=Quantity(Decimal("10")),
        tick_time=datetime.now(UTC),
    )
    assert event.event_type == EventType.MARKET_TICK_RECEIVED


def test_market_tick_received_without_quantity() -> None:
    event = MarketTickReceived(
        metadata=_METADATA,
        symbol="WTI",
        price=Price(Decimal("75.20")),
        tick_time=datetime.now(UTC),
    )
    assert event.quantity is None


def test_signal_generated() -> None:
    event = SignalGenerated(
        metadata=_METADATA,
        symbol="XAUUSD",
        direction="long",
        confidence=Confidence(Decimal("0.85")),
    )
    assert event.event_type == EventType.SIGNAL_GENERATED


def test_risk_alert() -> None:
    event = RiskAlert(
        metadata=_METADATA,
        message="max drawdown breached",
        severity=EventPriority.CRITICAL,
    )
    assert event.event_type == EventType.RISK_ALERT


def test_order_created() -> None:
    event = OrderCreated(
        metadata=_METADATA,
        symbol="WTI",
        quantity=Quantity(Decimal("5")),
        limit_price=Price(Decimal("74.00")),
    )
    assert event.event_type == EventType.ORDER_CREATED


def test_order_filled() -> None:
    event = OrderFilled(
        metadata=_METADATA,
        order_id=uuid4(),
        fill_price=Price(Decimal("74.05")),
        fill_quantity=Quantity(Decimal("5")),
    )
    assert event.event_type == EventType.ORDER_FILLED


def test_position_opened() -> None:
    event = PositionOpened(
        metadata=_METADATA,
        symbol="XAUUSD",
        quantity=Quantity(Decimal("2")),
        entry_price=Price(Decimal("1899.00")),
    )
    assert event.event_type == EventType.POSITION_OPENED


def test_position_closed() -> None:
    event = PositionClosed(
        metadata=_METADATA,
        position_id=uuid4(),
        exit_price=Price(Decimal("1910.00")),
        realized_pnl=Money(Decimal("22.00"), "USD"),
    )
    assert event.event_type == EventType.POSITION_CLOSED


def test_portfolio_updated() -> None:
    event = PortfolioUpdated(
        metadata=_METADATA,
        total_value=Money(Decimal("100000.00"), "USD"),
        as_of=datetime.now(UTC),
    )
    assert event.event_type == EventType.PORTFOLIO_UPDATED


def test_events_are_immutable() -> None:
    event = RiskAlert(metadata=_METADATA, message="x", severity=EventPriority.LOW)
    with pytest.raises(PydanticValidationError):
        event.message = "changed"  # type: ignore[misc]
