"""Subscription management for market data consumers.

Provides a higher-level, asset/timeframe-filtered subscription API on top
of the raw :class:`~quant_os.events.EventBus`, so consumers don't need to
filter event payloads themselves.
"""

from __future__ import annotations

import typing
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from quant_os.core.identifiers import TypedId
from quant_os.core.logging import get_logger
from quant_os.events import EventBus, EventType, MarketTickReceived, SubscriptionId
from quant_os.events.base import Event
from quant_os.market.events.market_events import CandleClosed, QuoteUpdated
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.timeframe import TimeFrame

_logger = get_logger(__name__)

MarketListener = Callable[[object], Awaitable[None]]
"""An async callable invoked with a matching market data event payload
(:class:`~quant_os.events.MarketTickReceived`,
:class:`~quant_os.market.events.market_events.QuoteUpdated`, or
:class:`~quant_os.market.events.market_events.CandleClosed`)."""


class MarketSubscriptionId(TypedId):
    """Opaque identifier for an active market data subscription."""


@dataclass(frozen=True, slots=True)
class SubscriptionFilter:
    """Filters controlling which events a subscription receives.

    Attributes:
        symbols: If non-empty, only events for these symbols are
            delivered. An empty set means "all symbols".
        timeframes: If non-empty, only candle events for these timeframes
            are delivered. Ignored for ticks and quotes, which have no
            timeframe. An empty set means "all timeframes".
    """

    symbols: frozenset[Symbol] = field(default_factory=frozenset[Symbol])
    timeframes: frozenset[TimeFrame] = field(default_factory=frozenset[TimeFrame])

    def matches_symbol(self, symbol: Symbol) -> bool:
        """Check whether a symbol passes this filter.

        Args:
            symbol: The symbol to check.

        Returns:
            True if this filter has no symbol restriction, or if
            ``symbol`` is in :attr:`symbols`.
        """
        return not self.symbols or symbol in self.symbols

    def matches_timeframe(self, timeframe: TimeFrame) -> bool:
        """Check whether a timeframe passes this filter.

        Args:
            timeframe: The timeframe to check.

        Returns:
            True if this filter has no timeframe restriction, or if
            ``timeframe`` is in :attr:`timeframes`.
        """
        return not self.timeframes or timeframe in self.timeframes


@dataclass(frozen=True, slots=True)
class _Subscription:
    listener: MarketListener
    filter: SubscriptionFilter


class SubscriptionManager:
    """Manages asset/timeframe-filtered subscriptions to market data.

    Internally subscribes once to the relevant event types on the
    :class:`~quant_os.events.EventBus`, then fans matching events out to
    each registered listener whose filter matches.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the subscription manager and wire it to the event bus.

        Args:
            event_bus: The event bus to subscribe to for tick, quote, and
                candle-close events.
        """
        self._event_bus = event_bus
        self._subscriptions: dict[MarketSubscriptionId, _Subscription] = {}
        self._bus_subscription_ids: list[SubscriptionId] = []

    async def start(self) -> None:
        """Begin listening to the underlying event bus.

        Must be called once before any listener will receive events.
        """
        self._bus_subscription_ids.append(
            await self._event_bus.subscribe(EventType.MARKET_TICK_RECEIVED, self._on_tick)
        )
        self._bus_subscription_ids.append(
            await self._event_bus.subscribe(EventType.QUOTE_UPDATED, self._on_quote)
        )
        self._bus_subscription_ids.append(
            await self._event_bus.subscribe(EventType.CANDLE_CLOSED, self._on_candle_closed)
        )

    async def stop(self) -> None:
        """Stop listening to the underlying event bus."""
        for subscription_id in self._bus_subscription_ids:
            await self._event_bus.unsubscribe(subscription_id)
        self._bus_subscription_ids.clear()

    def subscribe(
        self, listener: MarketListener, *, filter: SubscriptionFilter | None = None
    ) -> MarketSubscriptionId:
        """Register a listener for market data matching an optional filter.

        Args:
            listener: An async callable invoked with each matching event
                payload.
            filter: Restricts which events are delivered. Defaults to no
                restriction (all symbols, all timeframes).

        Returns:
            A subscription identifier usable with :meth:`unsubscribe`.
        """
        subscription_id = MarketSubscriptionId.generate()
        self._subscriptions[subscription_id] = _Subscription(
            listener=listener, filter=filter if filter is not None else SubscriptionFilter()
        )
        _logger.debug(
            "Market subscription registered",
            extra={"subscription_id": str(subscription_id)},
        )
        return subscription_id

    def unsubscribe(self, subscription_id: MarketSubscriptionId) -> None:
        """Remove a previously registered subscription.

        Args:
            subscription_id: The identifier returned by :meth:`subscribe`.
                Unsubscribing an unknown or already-removed identifier is
                a no-op.
        """
        self._subscriptions.pop(subscription_id, None)

    @property
    def listener_count(self) -> int:
        """The number of currently registered listeners.

        Returns:
            The count of active subscriptions.
        """
        return len(self._subscriptions)

    async def _on_tick(self, event: Event) -> None:
        tick_event = typing.cast("MarketTickReceived", event)
        symbol = Symbol(code=tick_event.symbol)
        for subscription in list(self._subscriptions.values()):
            if subscription.filter.matches_symbol(symbol):
                await subscription.listener(tick_event)

    async def _on_quote(self, event: Event) -> None:
        quote_event = typing.cast("QuoteUpdated", event)
        for subscription in list(self._subscriptions.values()):
            if subscription.filter.matches_symbol(quote_event.quote.symbol):
                await subscription.listener(quote_event)

    async def _on_candle_closed(self, event: Event) -> None:
        candle_event = typing.cast("CandleClosed", event)
        for subscription in list(self._subscriptions.values()):
            if subscription.filter.matches_symbol(
                candle_event.candle.symbol
            ) and subscription.filter.matches_timeframe(candle_event.candle.timeframe):
                await subscription.listener(candle_event)
