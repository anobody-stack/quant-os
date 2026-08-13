"""The Market Service: the single entry point for market data.

Responsibilities: request data from providers, validate it, normalize it
(providers already return QuantOS models, so normalization here is a
pass-through boundary — no provider-specific object ever reaches this
layer), publish events, store, and serve consumers.
"""

from __future__ import annotations

from datetime import datetime

from quant_os.core.exceptions import InfrastructureError, ValidationError
from quant_os.core.logging import get_logger
from quant_os.events import EventBus, EventMetadata, EventPriority, MarketTickReceived
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.events.market_events import (
    CandleClosed,
    HistoricalDataLoaded,
    ProviderConnected,
    ProviderDisconnected,
    QuoteUpdated,
)
from quant_os.market.interfaces.providers import (
    HistoricalDataProvider,
    MarketDataProvider,
    QuoteProvider,
)
from quant_os.market.interfaces.repositories import MarketRepository
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame
from quant_os.market.validation.validators import validate_quote, validate_tick

_logger = get_logger(__name__)
_SOURCE = "market.market_service"


class MarketService:
    """The single source of truth for market prices inside QuantOS.

    No other module should access a market data provider directly — every
    subsystem (AI, strategies, risk, portfolio, execution, reporting)
    consumes market data only through this service.
    """

    def __init__(
        self,
        provider: MarketDataProvider,
        repository: MarketRepository,
        cache: MarketCache,
        event_bus: EventBus,
    ) -> None:
        """Initialize the Market Service.

        Args:
            provider: The market data provider to source data from.
                Must also implement whichever of
                :class:`~quant_os.market.interfaces.providers.HistoricalDataProvider`
                and :class:`~quant_os.market.interfaces.providers.QuoteProvider`
                are needed by the methods called.
            repository: The repository to persist data to.
            cache: The cache to serve fast reads from.
            event_bus: The event bus to publish market events on.
        """
        self.provider = provider
        self.repository = repository
        self.cache = cache
        self.event_bus = event_bus

    async def connect(self) -> None:
        """Connect the underlying provider and publish a connectivity event."""
        await self.provider.connect()
        await self.event_bus.publish(
            ProviderConnected(
                metadata=EventMetadata(source=_SOURCE),
                provider_name=type(self.provider).__name__,
            )
        )
        _logger.info("Market provider connected", extra={"provider": type(self.provider).__name__})

    async def disconnect(self, *, reason: str = "") -> None:
        """Disconnect the underlying provider and publish a connectivity event.

        Args:
            reason: An optional human-readable reason for disconnecting.
        """
        await self.provider.disconnect()
        await self.event_bus.publish(
            ProviderDisconnected(
                metadata=EventMetadata(source=_SOURCE),
                provider_name=type(self.provider).__name__,
                reason=reason,
            )
        )
        _logger.info(
            "Market provider disconnected",
            extra={"provider": type(self.provider).__name__, "reason": reason},
        )

    async def ingest_tick(self, tick: Tick) -> None:
        """Validate, store, cache, and publish an incoming tick.

        Args:
            tick: The tick to ingest.

        Raises:
            quant_os.core.exceptions.ValidationError: If the tick fails
                validation (future timestamp or duplicate of the last
                accepted tick for its symbol).
        """
        last_tick = self.cache.get_latest_tick(tick.symbol)
        try:
            validate_tick(tick, last_tick=last_tick)
        except ValidationError:
            _logger.warning("Tick rejected by validation", extra={"symbol": tick.symbol.code})
            raise

        await self.repository.ticks.save(tick)
        self.cache.set_latest_tick(tick)
        await self.event_bus.publish(
            MarketTickReceived(
                metadata=EventMetadata(source=_SOURCE),
                symbol=tick.symbol.code,
                price=tick.price,
                quantity=tick.volume,
                tick_time=tick.timestamp,
            )
        )

    async def ingest_quote(self, quote: Quote) -> None:
        """Validate, store, cache, and publish an incoming quote.

        Args:
            quote: The quote to ingest.

        Raises:
            quant_os.core.exceptions.ValidationError: If the quote fails
                validation (future timestamp).
        """
        try:
            validate_quote(quote)
        except ValidationError:
            _logger.warning("Quote rejected by validation", extra={"symbol": quote.symbol.code})
            raise

        await self.repository.quotes.save(quote)
        self.cache.set_latest_quote(quote)
        await self.event_bus.publish(
            QuoteUpdated(metadata=EventMetadata(source=_SOURCE), quote=quote)
        )

    async def ingest_candle(self, candle: OHLCVCandle) -> None:
        """Store, cache, and publish a completed candle.

        OHLC internal consistency is already enforced by the
        :class:`~quant_os.market.models.candle.OHLCVCandle` model itself.

        Args:
            candle: The completed candle to ingest.
        """
        await self.repository.candles.save(candle)
        cached = self.cache.get_last_n_candles(candle.symbol, candle.timeframe, 500)
        self.cache.set_candles(candle.symbol, candle.timeframe, [*cached, candle])
        await self.event_bus.publish(
            CandleClosed(
                metadata=EventMetadata(source=_SOURCE, priority=EventPriority.LOW), candle=candle
            )
        )

    async def get_latest_price(self, symbol: Symbol) -> Tick | None:
        """Get the latest known tick for a symbol, preferring the cache.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest tick, from cache if available and unexpired,
            otherwise from the repository, or ``None`` if unknown.
        """
        cached = self.cache.get_latest_tick(symbol)
        if cached is not None:
            return cached
        stored = await self.repository.ticks.get_latest(symbol)
        if stored is not None:
            self.cache.set_latest_tick(stored)
        return stored

    async def get_latest_quote(self, symbol: Symbol) -> Quote | None:
        """Get the latest known quote for a symbol, preferring the cache.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest quote, from cache if available and unexpired,
            otherwise from the repository, or ``None`` if unknown.
        """
        cached = self.cache.get_latest_quote(symbol)
        if cached is not None:
            return cached
        stored = await self.repository.quotes.get_latest(symbol)
        if stored is not None:
            self.cache.set_latest_quote(stored)
        return stored

    async def get_historical_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: datetime,
        end: datetime,
    ) -> list[OHLCVCandle]:
        """Fetch historical candles, sourcing from the provider and storing them.

        Requires the configured provider to also implement
        :class:`~quant_os.market.interfaces.providers.HistoricalDataProvider`.

        Args:
            symbol: The instrument to fetch.
            timeframe: The bar granularity to fetch.
            start: The UTC start of the requested range, inclusive.
            end: The UTC end of the requested range, inclusive.

        Returns:
            Candles covering the requested range, oldest first.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the
                configured provider does not implement
                ``HistoricalDataProvider``.
        """
        if not isinstance(self.provider, HistoricalDataProvider):
            raise InfrastructureError(
                f"Provider {type(self.provider).__name__} does not support historical data"
            )
        candles = await self.provider.get_candles(symbol, timeframe, start=start, end=end)
        for candle in candles:
            await self.repository.candles.save(candle)
        self.cache.set_candles(symbol, timeframe, candles)
        await self.event_bus.publish(
            HistoricalDataLoaded(
                metadata=EventMetadata(source=_SOURCE),
                symbol=symbol,
                timeframe=timeframe.value,
                candle_count=len(candles),
            )
        )
        return candles

    async def fetch_and_ingest_quote(self, symbol: Symbol) -> Quote:
        """Fetch a fresh quote from the provider and ingest it.

        Requires the configured provider to also implement
        :class:`~quant_os.market.interfaces.providers.QuoteProvider`.

        Args:
            symbol: The instrument to fetch.

        Returns:
            The freshly fetched and ingested quote.

        Raises:
            quant_os.core.exceptions.InfrastructureError: If the
                configured provider does not implement ``QuoteProvider``.
        """
        if not isinstance(self.provider, QuoteProvider):
            raise InfrastructureError(
                f"Provider {type(self.provider).__name__} does not support quotes"
            )
        quote = await self.provider.get_quote(symbol)
        await self.ingest_quote(quote)
        return quote
