"""In-memory implementation of CandleRepository."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime

from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.timeframe import TimeFrame

_MAX_CANDLES_PER_SERIES = 10_000


class InMemoryCandleRepository:
    """An in-memory :class:`~quant_os.market.interfaces.repositories.CandleRepository`.

    Retains up to a bounded number of the most recent candles per
    symbol/timeframe pair, ordered by ``open_time``. Not persisted across
    process restarts.
    """

    def __init__(self) -> None:
        """Initialize an empty repository."""
        self._candles: dict[tuple[Symbol, TimeFrame], deque[OHLCVCandle]] = defaultdict(
            lambda: deque(maxlen=_MAX_CANDLES_PER_SERIES)
        )

    async def save(self, candle: OHLCVCandle) -> None:
        """Persist a candle, appending it to its symbol/timeframe series.

        Args:
            candle: The candle to persist.
        """
        self._candles[(candle.symbol, candle.timeframe)].append(candle)

    async def get_latest(self, symbol: Symbol, timeframe: TimeFrame) -> OHLCVCandle | None:
        """Retrieve the most recently stored candle for a symbol/timeframe.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.

        Returns:
            The latest stored candle, or ``None`` if none exists.
        """
        series = self._candles.get((symbol, timeframe))
        if not series:
            return None
        return series[-1]

    async def get_last_n(self, symbol: Symbol, timeframe: TimeFrame, n: int) -> list[OHLCVCandle]:
        """Retrieve the most recent ``n`` candles for a symbol/timeframe.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.
            n: Maximum number of candles to return.

        Returns:
            The most recent candles, oldest first.
        """
        series = self._candles.get((symbol, timeframe))
        if not series:
            return []
        return list(series)[-n:]

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
        series = self._candles.get((symbol, timeframe))
        if not series:
            return []
        return [candle for candle in series if start <= candle.open_time <= end]
