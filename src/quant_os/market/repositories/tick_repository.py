"""In-memory implementation of TickRepository."""

from __future__ import annotations

from collections import defaultdict, deque

from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick

_MAX_TICKS_PER_SYMBOL = 10_000


class InMemoryTickRepository:
    """An in-memory :class:`~quant_os.market.interfaces.repositories.TickRepository`.

    Retains up to a bounded number of the most recent ticks per symbol.
    Not persisted across process restarts.
    """

    def __init__(self) -> None:
        """Initialize an empty repository."""
        self._ticks: dict[Symbol, deque[Tick]] = defaultdict(
            lambda: deque(maxlen=_MAX_TICKS_PER_SYMBOL)
        )

    async def save(self, tick: Tick) -> None:
        """Persist a tick, appending it to the symbol's history.

        Args:
            tick: The tick to persist.
        """
        self._ticks[tick.symbol].append(tick)

    async def get_latest(self, symbol: Symbol) -> Tick | None:
        """Retrieve the most recently stored tick for a symbol.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest stored tick, or ``None`` if none exists.
        """
        history = self._ticks.get(symbol)
        if not history:
            return None
        return history[-1]

    async def list_recent(self, symbol: Symbol, limit: int = 100) -> list[Tick]:
        """List recently stored ticks for a symbol, most recent first.

        Args:
            symbol: The instrument to look up.
            limit: Maximum number of ticks to return.

        Returns:
            Stored ticks for ``symbol``, most recent first.
        """
        history = self._ticks.get(symbol)
        if not history:
            return []
        return list(reversed(history))[:limit]
