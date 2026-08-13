"""News repository interface.

This is an interface only — no storage backend (in-memory, database, etc.)
is implemented here. That is reserved for a later milestone.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from quant_os.events.domain_events import NewsReceived


@runtime_checkable
class NewsRepository(Protocol):
    """Abstraction for persisting and retrieving news articles."""

    async def save(self, article: NewsReceived) -> None:
        """Persist a news article.

        Args:
            article: The article to persist.
        """
        ...

    async def get_by_id(self, article_id: UUID) -> NewsReceived | None:
        """Retrieve a stored article by identifier.

        Args:
            article_id: Identifier of the article to look up.

        Returns:
            The stored article, or ``None`` if no article with that
            identifier exists.
        """
        ...

    async def list_recent(self, limit: int = 50) -> list[NewsReceived]:
        """List recently stored articles, most recent first.

        Args:
            limit: Maximum number of articles to return.

        Returns:
            Recently stored articles, most recent first.
        """
        ...

    async def delete(self, article_id: UUID) -> None:
        """Delete a stored article by identifier.

        Args:
            article_id: Identifier of the article to delete.
        """
        ...
