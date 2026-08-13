"""Market data provider interface.

This is an interface only — no concrete provider (broker feed, vendor API,
mock, etc.) is implemented here. That is reserved for a later milestone.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from quant_os.events.domain_events import MarketTickReceived


@runtime_checkable
class MarketDataProvider(Protocol):
    """Abstraction for a source of market data ticks.

    Every future implementation (broker feed, vendor API, mock, replay
    from storage, etc.) must be interchangeable behind this interface; no
    provider-specific detail may leak into calling code.
    """

    async def get_latest_tick(self, symbol: str) -> MarketTickReceived:
        """Fetch the most recent tick for a symbol.

        Args:
            symbol: The instrument symbol to fetch.

        Returns:
            The latest available tick for ``symbol``.
        """
        ...

    async def stream_ticks(self, symbol: str) -> AsyncIterator[MarketTickReceived]:
        """Stream ticks for a symbol as they occur.

        Args:
            symbol: The instrument symbol to stream.

        Returns:
            An asynchronous iterator yielding ticks for ``symbol`` as they
            arrive.
        """
        ...
