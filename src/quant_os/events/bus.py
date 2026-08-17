"""EventBus abstraction: publish/subscribe interface and supporting types."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

from quant_os.core.identifiers import TypedId
from quant_os.events.base import Event
from quant_os.events.enums import EventType

EventHandler = Callable[[Event], Awaitable[None]]
"""An async callable invoked with a published event."""

Middleware = Callable[[Event, EventHandler], Awaitable[None]]
"""An async callable wrapping event dispatch.

A middleware receives the event and the "next" handler in the chain, and
is responsible for calling ``await next_handler(event)`` itself (typically
after/around its own logic), enabling cross-cutting concerns such as
logging or metrics to wrap dispatch without the event bus knowing about
them.
"""


class SubscriptionId(TypedId):
    """Opaque identifier for an active event bus subscription."""


@runtime_checkable
class EventBus(Protocol):
    """Abstraction for publishing and subscribing to domain events.

    This is a pure interface: no transport, persistence, or delivery
    guarantees are implied. Concrete implementations (e.g.
    :class:`~quant_os.events.async_bus.AsyncEventBus`) define those semantics.
    """

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers of its event type.

        Args:
            event: The event to publish.
        """
        ...

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> SubscriptionId:
        """Register a handler to be invoked for events of a given type.

        Args:
            event_type: The event type to subscribe to.
            handler: An async callable invoked with each matching event.

        Returns:
            A subscription identifier that can later be passed to
            :meth:`unsubscribe`.
        """
        ...

    async def unsubscribe(self, subscription_id: SubscriptionId) -> None:
        """Remove a previously registered subscription.

        Args:
            subscription_id: The identifier returned by :meth:`subscribe`.
        """
        ...

    def add_middleware(self, middleware: Middleware) -> None:
        """Register a middleware to wrap all future event dispatch.

        Args:
            middleware: The middleware to add. Middlewares run in the
                order they were added, outermost first.
        """
        ...
