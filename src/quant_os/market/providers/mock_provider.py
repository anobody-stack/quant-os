"""A mock market data provider generating realistic synthetic data.

No network access, no HTTP requests — purely a deterministic (per-seed)
synthetic data generator, used for testing the Market Data Engine without
depending on any real external service.
"""

from __future__ import annotations

import random
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from decimal import Decimal

from quant_os.core.exceptions import InfrastructureError
from quant_os.core.time import utc_now
from quant_os.core.types import Price, Quantity
from quant_os.market.assets import get_supported_asset
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame

_DEFAULT_BASE_PRICES: dict[str, Decimal] = {
    "XAUUSD": Decimal("1950.00"),
    "WTIUSD": Decimal("78.50"),
    "BCOUSD": Decimal("82.30"),
    "EURUSD": Decimal("1.0850"),
}
_DEFAULT_SPREAD_BPS = Decimal("2")  # 2 basis points


class MockMarketDataProvider:
    """A synthetic market data provider for the four initially supported assets.

    Generates a deterministic random walk (seeded) for historical
    candles, quotes, and streamed ticks — no real market data, no network
    access. Implements every provider interface in
    :mod:`quant_os.market.interfaces.providers`.
    """

    def __init__(self, *, name: str = "mock", seed: int = 42) -> None:
        """Initialize the mock provider.

        Args:
            name: A label identifying this provider instance (used in
                connection/lifecycle events).
            seed: Random seed, for deterministic synthetic data across
                runs.
        """
        self.name = name
        self._rng = random.Random(seed)
        self._connected = False
        self._prices = dict(_DEFAULT_BASE_PRICES)

    async def connect(self) -> None:
        """Mark the provider as connected."""
        self._connected = True

    async def disconnect(self) -> None:
        """Mark the provider as disconnected."""
        self._connected = False

    async def is_connected(self) -> bool:
        """Report the provider's connection state.

        Returns:
            True if connected, False otherwise.
        """
        return self._connected

    async def get_quote(self, symbol: Symbol) -> Quote:
        """Generate a synthetic current quote for a symbol.

        Args:
            symbol: The instrument to quote.

        Returns:
            A synthetic :class:`~quant_os.market.models.quote.Quote`.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the provider
                is not connected, or the symbol is unsupported.
        """
        self._require_connected()
        self._require_supported(symbol)
        mid = self._walk_price(symbol)
        quantum = get_supported_asset(symbol).precision.tick_size
        spread = max((mid * _DEFAULT_SPREAD_BPS / Decimal("10000")), quantum)
        half_spread = ((spread / 2) / quantum).quantize(Decimal("1")) * quantum
        return Quote(
            symbol=symbol,
            bid=Price(mid - half_spread),
            ask=Price(mid + half_spread),
            timestamp=utc_now(),
        )

    async def stream_ticks(self, symbol: Symbol) -> AsyncIterator[Tick]:
        """Stream a synthetic, unending sequence of ticks for a symbol.

        Args:
            symbol: The instrument to stream.

        Yields:
            Synthetic :class:`~quant_os.market.models.tick.Tick` instances.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the provider
                is not connected, or the symbol is unsupported.
        """
        self._require_connected()
        self._require_supported(symbol)
        while True:
            price = self._walk_price(symbol)
            yield Tick(
                symbol=symbol,
                price=Price(price),
                volume=Quantity(Decimal(self._rng.randint(1, 100))),
                timestamp=utc_now(),
            )

    async def get_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: datetime,
        end: datetime,
    ) -> list[OHLCVCandle]:
        """Generate a synthetic candle series for a symbol/timeframe/range.

        Args:
            symbol: The instrument to generate candles for.
            timeframe: The bar granularity. Must have a fixed duration
                (not :attr:`~quant_os.market.models.timeframe.TimeFrame.TICK`
                or :attr:`~quant_os.market.models.timeframe.TimeFrame.MN1`).
            start: The UTC start of the requested range, inclusive.
            end: The UTC end of the requested range, inclusive.

        Returns:
            Synthetic candles covering the requested range, oldest first.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the provider
                is not connected, the symbol is unsupported, the
                timeframe has no fixed duration, or ``end`` precedes
                ``start``.
        """
        self._require_connected()
        self._require_supported(symbol)
        duration = timeframe.seconds
        if duration is None:
            raise InfrastructureError(
                f"Cannot generate historical candles for timeframe {timeframe.value!r}: "
                "no fixed duration",
                context={"timeframe": timeframe.value},
            )
        if end < start:
            raise InfrastructureError(
                "end must not precede start", context={"start": str(start), "end": str(end)}
            )

        candles: list[OHLCVCandle] = []
        cursor = start
        step = timedelta(seconds=duration)
        while cursor <= end:
            open_price = self._walk_price(symbol)
            high = open_price
            low = open_price
            for _ in range(4):
                sample = self._walk_price(symbol)
                high = max(high, sample)
                low = min(low, sample)
            close_price = self._walk_price(symbol)
            high = max(high, close_price)
            low = min(low, close_price)
            candles.append(
                OHLCVCandle(
                    symbol=symbol,
                    timeframe=timeframe,
                    open=Price(open_price),
                    high=Price(high),
                    low=Price(low),
                    close=Price(close_price),
                    volume=Quantity(Decimal(self._rng.randint(100, 10_000))),
                    open_time=cursor,
                    close_time=cursor + step,
                )
            )
            cursor += step
        return candles

    async def get_market_metadata(self, symbol: Symbol) -> MarketMetadata:
        """Generate synthetic market metadata for a symbol.

        Args:
            symbol: The instrument to describe.

        Returns:
            Synthetic :class:`~quant_os.market.models.market_metadata.MarketMetadata`
            describing the current state of ``symbol``'s market.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the provider
                is not connected, or the symbol is unsupported.
        """
        self._require_connected()
        self._require_supported(symbol)
        asset = get_supported_asset(symbol)
        status = await self.get_market_status(symbol)
        return MarketMetadata(asset=asset, status=status)

    async def get_market_status(self, symbol: Symbol) -> MarketStatus:
        """Report a synthetic market status for a symbol.

        Args:
            symbol: The instrument to check.

        Returns:
            Always :data:`~quant_os.market.models.market_status.MarketStatus.OPEN`
            while connected.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the provider
                is not connected, or the symbol is unsupported.
        """
        self._require_connected()
        self._require_supported(symbol)
        return MarketStatus.OPEN

    def _walk_price(self, symbol: Symbol) -> Decimal:
        """Advance and return this symbol's synthetic random-walk price.

        Args:
            symbol: The instrument to advance.

        Returns:
            The new mid price, quantized to the asset's price precision.
        """
        self._require_supported(symbol)
        current = self._prices[symbol.code]
        drift_bps = Decimal(self._rng.uniform(-5, 5))
        change = current * drift_bps / Decimal("10000")
        updated = max(current + change, Decimal("0.01"))
        quantum = get_supported_asset(symbol).precision.tick_size
        updated = (updated / quantum).quantize(Decimal("1")) * quantum
        self._prices[symbol.code] = updated
        return updated

    def _require_connected(self) -> None:
        """Raise if this provider is not currently connected."""
        if not self._connected:
            raise InfrastructureError(
                f"Provider {self.name!r} is not connected", context={"provider": self.name}
            )

    def _require_supported(self, symbol: Symbol) -> None:
        """Raise if ``symbol`` is not one of this provider's supported assets."""
        if symbol.code not in self._prices:
            raise InfrastructureError(
                f"Symbol {symbol.code!r} is not supported by provider {self.name!r}",
                context={"symbol": symbol.code, "provider": self.name},
            )
