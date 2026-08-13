"""Unit tests for AsyncEventBus."""

from __future__ import annotations

import pytest

from quant_os.core.exceptions import InfrastructureError
from quant_os.events.async_bus import AsyncEventBus
from quant_os.events.base import Event
from quant_os.events.bus import EventBus, SubscriptionId
from quant_os.events.domain_events import RiskAlert
from quant_os.events.enums import EventPriority, EventType
from quant_os.events.metadata import EventMetadata


def _make_alert(message: str = "test alert") -> RiskAlert:
    return RiskAlert(
        metadata=EventMetadata(source="test"),
        message=message,
        severity=EventPriority.HIGH,
    )


class TestPublishSubscribe:
    async def test_subscriber_receives_published_event(self) -> None:
        bus = AsyncEventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        await bus.subscribe(EventType.RISK_ALERT, handler)
        alert = _make_alert()
        await bus.publish(alert)

        assert received == [alert]

    async def test_multiple_subscribers_all_receive_event(self) -> None:
        bus = AsyncEventBus()
        received_a: list[Event] = []
        received_b: list[Event] = []

        async def handler_a(event: Event) -> None:
            received_a.append(event)

        async def handler_b(event: Event) -> None:
            received_b.append(event)

        await bus.subscribe(EventType.RISK_ALERT, handler_a)
        await bus.subscribe(EventType.RISK_ALERT, handler_b)
        alert = _make_alert()
        await bus.publish(alert)

        assert received_a == [alert]
        assert received_b == [alert]

    async def test_subscriber_only_receives_matching_event_type(self) -> None:
        bus = AsyncEventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        await bus.subscribe(EventType.NEWS_RECEIVED, handler)
        await bus.publish(_make_alert())

        assert received == []

    async def test_publish_with_no_subscribers_is_a_no_op(self) -> None:
        bus = AsyncEventBus()
        await bus.publish(_make_alert())  # must not raise

    async def test_conforms_to_event_bus_protocol(self) -> None:
        bus = AsyncEventBus()
        assert isinstance(bus, EventBus)


class TestUnsubscribe:
    async def test_unsubscribed_handler_no_longer_receives_events(self) -> None:
        bus = AsyncEventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        subscription_id = await bus.subscribe(EventType.RISK_ALERT, handler)
        await bus.unsubscribe(subscription_id)
        await bus.publish(_make_alert())

        assert received == []

    async def test_unsubscribing_unknown_id_is_a_no_op(self) -> None:
        bus = AsyncEventBus()
        await bus.unsubscribe(SubscriptionId.generate())  # must not raise

    async def test_unsubscribing_twice_is_a_no_op(self) -> None:
        bus = AsyncEventBus()

        async def handler(event: Event) -> None:
            pass

        subscription_id = await bus.subscribe(EventType.RISK_ALERT, handler)
        await bus.unsubscribe(subscription_id)
        await bus.unsubscribe(subscription_id)  # must not raise


class TestMiddleware:
    async def test_middleware_runs_around_dispatch(self) -> None:
        bus = AsyncEventBus()
        call_order: list[str] = []

        async def middleware(event: Event, next_handler: object) -> None:
            call_order.append("before")
            await next_handler(event)  # type: ignore[operator]
            call_order.append("after")

        async def handler(event: Event) -> None:
            call_order.append("handled")

        bus.add_middleware(middleware)
        await bus.subscribe(EventType.RISK_ALERT, handler)
        await bus.publish(_make_alert())

        assert call_order == ["before", "handled", "after"]

    async def test_multiple_middlewares_run_outermost_first(self) -> None:
        bus = AsyncEventBus()
        call_order: list[str] = []

        async def outer(event: Event, next_handler: object) -> None:
            call_order.append("outer-before")
            await next_handler(event)  # type: ignore[operator]
            call_order.append("outer-after")

        async def inner(event: Event, next_handler: object) -> None:
            call_order.append("inner-before")
            await next_handler(event)  # type: ignore[operator]
            call_order.append("inner-after")

        bus.add_middleware(outer)
        bus.add_middleware(inner)
        await bus.publish(_make_alert())

        assert call_order == ["outer-before", "inner-before", "inner-after", "outer-after"]

    async def test_middleware_can_short_circuit(self) -> None:
        bus = AsyncEventBus()
        handled = False

        async def blocking_middleware(event: Event, next_handler: object) -> None:
            # Deliberately does not call next_handler.
            pass

        async def handler(event: Event) -> None:
            nonlocal handled
            handled = True

        bus.add_middleware(blocking_middleware)
        await bus.subscribe(EventType.RISK_ALERT, handler)
        await bus.publish(_make_alert())

        assert handled is False


class TestErrorHandling:
    async def test_failing_handler_raises_infrastructure_error(self) -> None:
        bus = AsyncEventBus()

        async def failing_handler(event: Event) -> None:
            raise ValueError("boom")

        await bus.subscribe(EventType.RISK_ALERT, failing_handler)

        with pytest.raises(InfrastructureError):
            await bus.publish(_make_alert())

    async def test_other_handlers_still_run_when_one_fails(self) -> None:
        bus = AsyncEventBus()
        received: list[Event] = []

        async def failing_handler(event: Event) -> None:
            raise ValueError("boom")

        async def succeeding_handler(event: Event) -> None:
            received.append(event)

        await bus.subscribe(EventType.RISK_ALERT, failing_handler)
        await bus.subscribe(EventType.RISK_ALERT, succeeding_handler)

        with pytest.raises(InfrastructureError):
            await bus.publish(_make_alert())

        assert len(received) == 1
