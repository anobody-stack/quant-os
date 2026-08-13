"""Market data repository interfaces.

These are contracts only; see :mod:`quant_os.market.repositories` for
the in-memory implementations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame


@runtime_checkable
class TickRepository(Protocol):
    """Abstraction for persisting and retrieving ticks."""

    async def save(self, tick: Tick) -> None:
        """Persist a tick.

        Args:
            tick: The tick to persist.
        """
        ...

    async def get_latest(self, symbol: Symbol) -> Tick | None:
        """Retrieve the most recently stored tick for a symbol.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest stored tick, or ``None`` if none exists.
        """
        ...

    async def list_recent(self, symbol: Symbol, limit: int = 100) -> list[Tick]:
        """List recently stored ticks for a symbol, most recent first.

        Args:
            symbol: The instrument to look up.
            limit: Maximum number of ticks to return.

        Returns:
            Stored ticks for ``symbol``, most recent first.
        """
        ...


@runtime_checkable
class QuoteRepository(Protocol):
    """Abstraction for persisting and retrieving quotes."""

    async def save(self, quote: Quote) -> None:
        """Persist a quote.

        Args:
            quote: The quote to persist.
        """
        ...

    async def get_latest(self, symbol: Symbol) -> Quote | None:
        """Retrieve the most recently stored quote for a symbol.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest stored quote, or ``None`` if none exists.
        """
        ...


@runtime_checkable
class CandleRepository(Protocol):
    """Abstraction for persisting and retrieving OHLCV candles."""

    async def save(self, candle: OHLCVCandle) -> None:
        """Persist a candle.

        Args:
            candle: The candle to persist.
        """
        ...

    async def get_latest(self, symbol: Symbol, timeframe: TimeFrame) -> OHLCVCandle | None:
        """Retrieve the most recently stored candle for a symbol/timeframe.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.

        Returns:
            The latest stored candle, or ``None`` if none exists.
        """
        ...

    async def get_last_n(self, symbol: Symbol, timeframe: TimeFrame, n: int) -> list[OHLCVCandle]:
        """Retrieve the most recent ``n`` candles for a symbol/timeframe.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.
            n: Maximum number of candles to return.

        Returns:
            The most recent candles, oldest first.
        """
        ...

    async def get_range(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: datetime,
        end: datetime,
    ) -> list[OHLCVCandle]:
        """Retrieve candles for a symbol/timeframe within a time range.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.
            start: The UTC start of the requested range, inclusive.
            end: The UTC end of the requested range, inclusive.

        Returns:
            Candles covering the requested range, oldest first.
        """
        ...


@runtime_checkable
class MetadataRepository(Protocol):
    """Abstraction for persisting and retrieving market metadata."""

    async def save(self, metadata: MarketMetadata) -> None:
        """Persist a market metadata snapshot.

        Args:
            metadata: The metadata to persist.
        """
        ...

    async def get(self, symbol: Symbol) -> MarketMetadata | None:
        """Retrieve the most recently stored metadata for a symbol.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest stored metadata, or ``None`` if none exists.
        """
        ...


@runtime_checkable
class MarketRepository(Protocol):
    """A composite facade over the individual tick/quote/candle/metadata
    repositories, for consumers that want a single dependency rather than
    four.

    The sub-repositories are exposed as read-only properties rather than
    plain attributes so that any structurally compatible implementation
    (regardless of its own attribute vs. property choice) satisfies this
    Protocol under static type checking.
    """

    @property
    def ticks(self) -> TickRepository:
        """The tick repository."""
        ...

    @property
    def quotes(self) -> QuoteRepository:
        """The quote repository."""
        ...

    @property
    def candles(self) -> CandleRepository:
        """The candle repository."""
        ...

    @property
    def metadata(self) -> MetadataRepository:
        """The metadata repository."""
        ...
