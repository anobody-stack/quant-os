"""In-memory implementation of QuoteRepository."""

from __future__ import annotations

from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol


class InMemoryQuoteRepository:
    """An in-memory :class:`~quant_os.market.interfaces.repositories.QuoteRepository`.

    Retains only the latest quote per symbol. Not persisted across
    process restarts.
    """

    def __init__(self) -> None:
        """Initialize an empty repository."""
        self._latest: dict[Symbol, Quote] = {}

    async def save(self, quote: Quote) -> None:
        """Persist a quote, replacing any previously stored quote for its symbol.

        Args:
            quote: The quote to persist.
        """
        self._latest[quote.symbol] = quote

    async def get_latest(self, symbol: Symbol) -> Quote | None:
        """Retrieve the most recently stored quote for a symbol.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest stored quote, or ``None`` if none exists.
        """
        return self._latest.get(symbol)
