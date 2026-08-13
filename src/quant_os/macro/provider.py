"""Macro/economic calendar provider interface.

This is an interface only — no concrete provider (TradingEconomics, FRED,
central bank calendars, mock, etc.) is implemented here. That is reserved
for a later milestone.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from quant_os.events.domain_events import EconomicEventReceived


@runtime_checkable
class MacroProvider(Protocol):
    """Abstraction for a source of macroeconomic/calendar events.

    Every future implementation must be interchangeable behind this
    interface; no provider-specific detail may leak into calling code.
    """

    async def get_upcoming_events(self, limit: int = 50) -> list[EconomicEventReceived]:
        """Fetch upcoming scheduled economic events.

        Args:
            limit: Maximum number of events to return.

        Returns:
            Upcoming economic events, soonest first.
        """
        ...

    async def stream(self) -> AsyncIterator[EconomicEventReceived]:
        """Stream economic events as they are published or updated.

        Returns:
            An asynchronous iterator yielding events as they arrive.
        """
        ...
