"""In-memory implementation of the composite MarketRepository facade."""

from __future__ import annotations

from quant_os.market.repositories.candle_repository import InMemoryCandleRepository
from quant_os.market.repositories.metadata_repository import InMemoryMetadataRepository
from quant_os.market.repositories.quote_repository import InMemoryQuoteRepository
from quant_os.market.repositories.tick_repository import InMemoryTickRepository


class InMemoryMarketRepository:
    """A composite, in-memory :class:`~quant_os.market.interfaces.repositories.MarketRepository`.

    Bundles a tick, quote, candle, and metadata repository behind a
    single dependency, for consumers that don't need to depend on each
    individually.
    """

    def __init__(
        self,
        *,
        ticks: InMemoryTickRepository | None = None,
        quotes: InMemoryQuoteRepository | None = None,
        candles: InMemoryCandleRepository | None = None,
        metadata: InMemoryMetadataRepository | None = None,
    ) -> None:
        """Initialize the composite repository.

        Args:
            ticks: The tick repository to use. A fresh
                :class:`InMemoryTickRepository` is created if not provided.
            quotes: The quote repository to use. A fresh
                :class:`InMemoryQuoteRepository` is created if not provided.
            candles: The candle repository to use. A fresh
                :class:`InMemoryCandleRepository` is created if not provided.
            metadata: The metadata repository to use. A fresh
                :class:`InMemoryMetadataRepository` is created if not
                provided.
        """
        self.ticks = ticks if ticks is not None else InMemoryTickRepository()
        self.quotes = quotes if quotes is not None else InMemoryQuoteRepository()
        self.candles = candles if candles is not None else InMemoryCandleRepository()
        self.metadata = metadata if metadata is not None else InMemoryMetadataRepository()
