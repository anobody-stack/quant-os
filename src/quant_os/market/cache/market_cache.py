"""Market data cache: latest-value and windowed caching with TTL support."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from quant_os.core.time import utc_now
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame

_DEFAULT_TTL = timedelta(seconds=5)
_DEFAULT_CANDLE_HISTORY = 500


@dataclass(slots=True)
class _Entry[T]:
    """A cached value with the UTC time it was cached."""

    value: T
    cached_at: datetime


class MarketCache:
    """An in-memory cache of the latest market data, with TTL-based expiry.

    Caches the latest tick, latest quote, and a rolling window of recent
    candles per symbol/timeframe, plus market metadata. Reads past the
    configured TTL are treated as cache misses.
    """

    def __init__(
        self,
        *,
        ttl: timedelta = _DEFAULT_TTL,
        candle_history: int = _DEFAULT_CANDLE_HISTORY,
    ) -> None:
        """Initialize an empty cache.

        Args:
            ttl: How long a cached entry remains valid before being
                treated as expired.
            candle_history: How many recent candles to retain per
                symbol/timeframe.
        """
        self._ttl = ttl
        self._candle_history = candle_history
        self._latest_tick: dict[Symbol, _Entry[Tick]] = {}
        self._latest_quote: dict[Symbol, _Entry[Quote]] = {}
        self._candles: dict[tuple[Symbol, TimeFrame], _Entry[list[OHLCVCandle]]] = {}
        self._metadata: dict[Symbol, _Entry[MarketMetadata]] = {}

    def set_latest_tick(self, tick: Tick) -> None:
        """Cache the latest tick for its symbol.

        Args:
            tick: The tick to cache.
        """
        self._latest_tick[tick.symbol] = _Entry(tick, utc_now())

    def get_latest_tick(self, symbol: Symbol) -> Tick | None:
        """Retrieve the cached latest tick for a symbol, if not expired.

        Args:
            symbol: The instrument to look up.

        Returns:
            The cached tick, or ``None`` if absent or expired.
        """
        return self._get(self._latest_tick, symbol)

    def set_latest_quote(self, quote: Quote) -> None:
        """Cache the latest quote for its symbol.

        Args:
            quote: The quote to cache.
        """
        self._latest_quote[quote.symbol] = _Entry(quote, utc_now())

    def get_latest_quote(self, symbol: Symbol) -> Quote | None:
        """Retrieve the cached latest quote for a symbol, if not expired.

        Args:
            symbol: The instrument to look up.

        Returns:
            The cached quote, or ``None`` if absent or expired.
        """
        return self._get(self._latest_quote, symbol)

    def set_candles(self, symbol: Symbol, timeframe: TimeFrame, candles: list[OHLCVCandle]) -> None:
        """Cache a window of recent candles for a symbol/timeframe.

        Args:
            symbol: The instrument the candles belong to.
            timeframe: The bar granularity.
            candles: The candles to cache, oldest first. Only the most
                recent ``candle_history`` entries are retained.
        """
        trimmed = candles[-self._candle_history :]
        self._candles[(symbol, timeframe)] = _Entry(trimmed, utc_now())

    def get_latest_candle(self, symbol: Symbol, timeframe: TimeFrame) -> OHLCVCandle | None:
        """Retrieve the most recent cached candle for a symbol/timeframe.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.

        Returns:
            The latest cached candle, or ``None`` if absent, expired, or
            empty.
        """
        candles = self._get(self._candles, (symbol, timeframe))
        if not candles:
            return None
        return candles[-1]

    def get_last_n_candles(self, symbol: Symbol, timeframe: TimeFrame, n: int) -> list[OHLCVCandle]:
        """Retrieve the most recent ``n`` cached candles for a symbol/timeframe.

        Args:
            symbol: The instrument to look up.
            timeframe: The bar granularity to look up.
            n: Maximum number of candles to return.

        Returns:
            The most recent cached candles, oldest first, or an empty
            list if absent or expired.
        """
        candles = self._get(self._candles, (symbol, timeframe))
        if not candles:
            return []
        return candles[-n:]

    def set_metadata(self, metadata: MarketMetadata) -> None:
        """Cache market metadata for its asset's symbol.

        Args:
            metadata: The metadata to cache.
        """
        self._metadata[metadata.asset.symbol] = _Entry(metadata, utc_now())

    def get_metadata(self, symbol: Symbol) -> MarketMetadata | None:
        """Retrieve cached market metadata for a symbol, if not expired.

        Args:
            symbol: The instrument to look up.

        Returns:
            The cached metadata, or ``None`` if absent or expired.
        """
        return self._get(self._metadata, symbol)

    def invalidate(self, symbol: Symbol) -> None:
        """Invalidate all cached entries for a symbol (all timeframes included).

        Args:
            symbol: The instrument to invalidate.
        """
        self._latest_tick.pop(symbol, None)
        self._latest_quote.pop(symbol, None)
        self._metadata.pop(symbol, None)
        for key in [key for key in self._candles if key[0] == symbol]:
            del self._candles[key]

    def clear(self) -> None:
        """Invalidate every cached entry, for every symbol."""
        self._latest_tick.clear()
        self._latest_quote.clear()
        self._candles.clear()
        self._metadata.clear()

    def _get[K, V](self, store: dict[K, _Entry[V]], key: K) -> V | None:
        """Look up a cache entry, applying TTL expiry.

        Args:
            store: The backing dict for this cache category.
            key: The lookup key.

        Returns:
            The cached value, or ``None`` if absent or expired. An
            expired entry is evicted as a side effect.
        """
        entry = store.get(key)
        if entry is None:
            return None
        if utc_now() - entry.cached_at > self._ttl:
            del store[key]
            return None
        return entry.value
