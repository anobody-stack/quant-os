"""Market data provider interfaces.

These are contracts only — no implementations here. See
:mod:`quant_os.market.providers` for the mock implementation used for
testing.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Protocol, runtime_checkable

from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame


@runtime_checkable
class MarketDataProvider(Protocol):
    """The umbrella capability every market data provider must offer:
    connectivity lifecycle plus current market status.
    """

    async def connect(self) -> None:
        """Establish a connection to the underlying data source."""
        ...

    async def disconnect(self) -> None:
        """Tear down the connection to the underlying data source."""
        ...

    async def is_connected(self) -> bool:
        """Report whether the provider currently holds a live connection.

        Returns:
            True if connected, False otherwise.
        """
        ...


@runtime_checkable
class HistoricalDataProvider(Protocol):
    """Abstraction for a source of historical OHLCV candles."""

    async def get_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: datetime,
        end: datetime,
    ) -> list[OHLCVCandle]:
        """Fetch historical candles for a symbol over a time range.

        Args:
            symbol: The instrument to fetch.
            timeframe: The bar granularity to fetch.
            start: The UTC start of the requested range, inclusive.
            end: The UTC end of the requested range, inclusive.

        Returns:
            Candles covering the requested range, ordered oldest first.
        """
        ...


@runtime_checkable
class StreamingProvider(Protocol):
    """Abstraction for a source of live, streaming ticks."""

    async def stream_ticks(self, symbol: Symbol) -> AsyncIterator[Tick]:
        """Stream ticks for a symbol as they occur.

        Args:
            symbol: The instrument to stream.

        Returns:
            An asynchronous iterator yielding ticks as they arrive.
        """
        ...


@runtime_checkable
class QuoteProvider(Protocol):
    """Abstraction for a source of current bid/ask quotes."""

    async def get_quote(self, symbol: Symbol) -> Quote:
        """Fetch the current quote for a symbol.

        Args:
            symbol: The instrument to fetch.

        Returns:
            The current :class:`~quant_os.market.models.quote.Quote`.
        """
        ...


@runtime_checkable
class MetadataProvider(Protocol):
    """Abstraction for a source of market metadata (status, sessions)."""

    async def get_market_metadata(self, symbol: Symbol) -> MarketMetadata:
        """Fetch current market metadata for a symbol.

        Args:
            symbol: The instrument to fetch.

        Returns:
            The current
            :class:`~quant_os.market.models.market_metadata.MarketMetadata`.
        """
        ...

    async def get_market_status(self, symbol: Symbol) -> MarketStatus:
        """Fetch the current trading status for a symbol's market.

        Args:
            symbol: The instrument to fetch.

        Returns:
            The current :class:`~quant_os.market.models.market_status.MarketStatus`.
        """
        ...
