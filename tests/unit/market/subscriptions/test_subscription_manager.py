"""Unit tests for SubscriptionManager and SubscriptionFilter."""

from datetime import UTC, datetime
from decimal import Decimal

from quant_os.core.types import Price
from quant_os.events import AsyncEventBus, EventMetadata
from quant_os.events.domain_events import MarketTickReceived
from quant_os.market.events.market_events import QuoteUpdated
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.subscriptions.subscription_manager import (
    SubscriptionFilter,
    SubscriptionManager,
)

_XAU = Symbol(code="XAUUSD")
_EUR = Symbol(code="EURUSD")
_NOW = datetime.now(UTC)


class TestSubscriptionFilter:
    def test_empty_filter_matches_everything(self) -> None:
        filter_ = SubscriptionFilter()
        assert filter_.matches_symbol(_XAU)

    def test_symbol_filter_restricts(self) -> None:
        filter_ = SubscriptionFilter(symbols=frozenset({_XAU}))
        assert filter_.matches_symbol(_XAU)
        assert not filter_.matches_symbol(_EUR)


class TestSubscriptionManager:
    async def test_listener_receives_tick_for_matching_symbol(self) -> None:
        bus = AsyncEventBus()
        manager = SubscriptionManager(bus)
        await manager.start()
        received: list[object] = []

        async def listener(event: object) -> None:
            received.append(event)

        manager.subscribe(listener, filter=SubscriptionFilter(symbols=frozenset({_XAU})))
        await bus.publish(
            MarketTickReceived(
                metadata=EventMetadata(source="test"),
                symbol="XAUUSD",
                price=Price(Decimal("1900")),
                tick_time=_NOW,
            )
        )
        assert len(received) == 1

    async def test_listener_does_not_receive_non_matching_symbol(self) -> None:
        bus = AsyncEventBus()
        manager = SubscriptionManager(bus)
        await manager.start()
        received: list[object] = []

        async def listener(event: object) -> None:
            received.append(event)

        manager.subscribe(listener, filter=SubscriptionFilter(symbols=frozenset({_EUR})))
        await bus.publish(
            MarketTickReceived(
                metadata=EventMetadata(source="test"),
                symbol="XAUUSD",
                price=Price(Decimal("1900")),
                tick_time=_NOW,
            )
        )
        assert received == []

    async def test_listener_receives_quote_updates(self) -> None:
        bus = AsyncEventBus()
        manager = SubscriptionManager(bus)
        await manager.start()
        received: list[object] = []

        async def listener(event: object) -> None:
            received.append(event)

        manager.subscribe(listener)
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
        )
        await bus.publish(QuoteUpdated(metadata=EventMetadata(source="test"), quote=quote))
        assert len(received) == 1

    async def test_unsubscribe_stops_delivery(self) -> None:
        bus = AsyncEventBus()
        manager = SubscriptionManager(bus)
        await manager.start()
        received: list[object] = []

        async def listener(event: object) -> None:
            received.append(event)

        subscription_id = manager.subscribe(listener)
        manager.unsubscribe(subscription_id)
        await bus.publish(
            MarketTickReceived(
                metadata=EventMetadata(source="test"),
                symbol="XAUUSD",
                price=Price(Decimal("1900")),
                tick_time=_NOW,
            )
        )
        assert received == []

    async def test_listener_count(self) -> None:
        bus = AsyncEventBus()
        manager = SubscriptionManager(bus)

        async def listener(event: object) -> None:
            pass

        assert manager.listener_count == 0
        manager.subscribe(listener)
        assert manager.listener_count == 1

    async def test_stop_unsubscribes_from_bus(self) -> None:
        bus = AsyncEventBus()
        manager = SubscriptionManager(bus)
        await manager.start()
        await manager.stop()
        received: list[object] = []

        async def listener(event: object) -> None:
            received.append(event)

        manager.subscribe(listener)
        await bus.publish(
            MarketTickReceived(
                metadata=EventMetadata(source="test"),
                symbol="XAUUSD",
                price=Price(Decimal("1900")),
                tick_time=_NOW,
            )
        )
        assert received == []
