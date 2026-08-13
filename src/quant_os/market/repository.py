"""Market data repository interface.

This is an interface only — no storage backend (in-memory, database, etc.)
is implemented here. That is reserved for a later milestone.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from quant_os.events.domain_events import MarketTickReceived


@runtime_checkable
class MarketRepository(Protocol):
    """Abstraction for persisting and retrieving market data ticks."""

    async def save(self, tick: MarketTickReceived) -> None:
        """Persist a market tick.

        Args:
            tick: The tick to persist.
        """
        ...

    async def get_latest(self, symbol: str) -> MarketTickReceived | None:
        """Retrieve the most recently stored tick for a symbol.

        Args:
            symbol: The instrument symbol to look up.

        Returns:
            The latest stored tick for ``symbol``, or ``None`` if none
            exists.
        """
        ...

    async def list_by_symbol(self, symbol: str, limit: int = 100) -> list[MarketTickReceived]:
        """List stored ticks for a symbol, most recent first.

        Args:
            symbol: The instrument symbol to look up.
            limit: Maximum number of ticks to return.

        Returns:
            Stored ticks for ``symbol``, most recent first.
        """
        ...

    async def delete(self, tick_id: UUID) -> None:
        """Delete a stored tick by identifier.

        Args:
            tick_id: Identifier of the tick to delete.
        """
        ...
