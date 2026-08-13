"""In-memory, asyncio-based implementation of the EventBus interface.

No external broker or message queue is involved: subscribers live in
process memory for the lifetime of the bus instance.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

from quant_os.core.exceptions import InfrastructureError
from quant_os.core.logging import get_logger
from quant_os.events.base import Event
from quant_os.events.bus import EventBus, EventHandler, Middleware, SubscriptionId
from quant_os.events.enums import EventType

_logger = get_logger(__name__)


class AsyncEventBus(EventBus):
    """An in-memory, asyncio-native publish/subscribe event bus.

    Handlers subscribed to an event type are invoked concurrently
    (via :func:`asyncio.gather`) when a matching event is published.
    Middleware wraps the entire dispatch step, outermost-first in the
    order it was added.
    """

    def __init__(self) -> None:
        """Initialize an empty event bus with no subscribers or middleware."""
        self._handlers: dict[EventType, dict[SubscriptionId, EventHandler]] = defaultdict(dict)
        self._subscription_types: dict[SubscriptionId, EventType] = {}
        self._middleware: list[Middleware] = []

    async def publish(self, event: Event) -> None:
        """Publish an event through the middleware chain to all subscribers.

        Args:
            event: The event to publish.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If one or more
                subscriber handlers raise an exception. All handlers are
                still given a chance to run; failures are aggregated.
        """
        chain = self._build_chain()
        await chain(event)

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> SubscriptionId:
        """Register a handler for a given event type.

        Args:
            event_type: The event type to subscribe to.
            handler: An async callable invoked with each matching event.

        Returns:
            A subscription identifier usable with :meth:`unsubscribe`.
        """
        subscription_id = SubscriptionId.generate()
        self._handlers[event_type][subscription_id] = handler
        self._subscription_types[subscription_id] = event_type
        _logger.debug(
            "Subscribed handler to event type",
            extra={"event_type": event_type.value, "subscription_id": str(subscription_id)},
        )
        return subscription_id

    async def unsubscribe(self, subscription_id: SubscriptionId) -> None:
        """Remove a previously registered subscription.

        Args:
            subscription_id: The identifier returned by :meth:`subscribe`.
                Unsubscribing an unknown or already-removed identifier is a
                no-op.
        """
        event_type = self._subscription_types.pop(subscription_id, None)
        if event_type is None:
            return
        self._handlers[event_type].pop(subscription_id, None)
        _logger.debug(
            "Unsubscribed handler from event type",
            extra={"event_type": event_type.value, "subscription_id": str(subscription_id)},
        )

    def add_middleware(self, middleware: Middleware) -> None:
        """Register a middleware to wrap all future event dispatch.

        Args:
            middleware: The middleware to add. Middlewares run in the
                order they were added, outermost first.
        """
        self._middleware.append(middleware)

    def _build_chain(self) -> EventHandler:
        """Build the full dispatch chain: middleware wrapped around fan-out.

        Returns:
            A single async callable representing the full middleware chain
            terminating in :meth:`_dispatch`.
        """
        handler: EventHandler = self._dispatch
        for middleware in reversed(self._middleware):
            handler = self._wrap(middleware, handler)
        return handler

    @staticmethod
    def _wrap(middleware: Middleware, next_handler: EventHandler) -> EventHandler:
        """Wrap a single middleware around the next handler in the chain.

        Args:
            middleware: The middleware to apply.
            next_handler: The handler the middleware should invoke.

        Returns:
            An async callable that applies ``middleware`` around
            ``next_handler``.
        """

        async def wrapped(event: Event) -> None:
            await middleware(event, next_handler)

        return wrapped

    async def _dispatch(self, event: Event) -> None:
        """Fan an event out to all subscribers of its event type.

        Args:
            event: The event to dispatch.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If one or more
                subscriber handlers raise an exception.
        """
        handlers = list(self._handlers.get(event.event_type, {}).values())
        if not handlers:
            _logger.debug(
                "No subscribers for event type", extra={"event_type": event.event_type.value}
            )
            return

        results = await asyncio.gather(
            *(handler(event) for handler in handlers), return_exceptions=True
        )
        failures = [result for result in results if isinstance(result, BaseException)]
        for failure in failures:
            _logger.error(
                "Event handler raised an exception",
                extra={"event_type": event.event_type.value, "error": str(failure)},
            )
        if failures:
            raise InfrastructureError(
                f"{len(failures)} of {len(handlers)} handler(s) failed for event type "
                f"{event.event_type.value!r}",
                cause=failures[0] if isinstance(failures[0], Exception) else None,
                context={"event_type": event.event_type.value, "failure_count": len(failures)},
            )
