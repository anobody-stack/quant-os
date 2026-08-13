"""News provider interface.

This is an interface only — no concrete provider (Reuters, Bloomberg,
NewsAPI, RSS, mock, etc.) is implemented here. That is reserved for a
later milestone.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from quant_os.events.domain_events import NewsReceived


@runtime_checkable
class NewsProvider(Protocol):
    """Abstraction for a source of financial news.

    Every future implementation must be interchangeable behind this
    interface; no provider-specific detail may leak into calling code.
    """

    async def get_latest_headlines(self, limit: int = 50) -> list[NewsReceived]:
        """Fetch the most recent headlines.

        Args:
            limit: Maximum number of headlines to return.

        Returns:
            The most recent available headlines, most recent first.
        """
        ...

    async def stream(self) -> AsyncIterator[NewsReceived]:
        """Stream news articles as they are published.

        Returns:
            An asynchronous iterator yielding articles as they arrive.
        """
        ...
