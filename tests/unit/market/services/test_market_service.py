"""Unit tests for MarketService."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from quant_os.core.exceptions import InfrastructureError, ValidationError
from quant_os.core.types import Price, Quantity
from quant_os.events import AsyncEventBus
from quant_os.events.enums import EventType
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.events.market_events import ProviderConnected
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame
from quant_os.market.providers.mock_provider import MockMarketDataProvider
from quant_os.market.repositories.market_repository import InMemoryMarketRepository
from quant_os.market.services.market_service import MarketService

_XAU = Symbol(code="XAUUSD")
_NOW = datetime.now(UTC)


def _make_service() -> MarketService:
    return MarketService(
        MockMarketDataProvider(),
        InMemoryMarketRepository(),
        MarketCache(),
        AsyncEventBus(),
    )


def _tick(price: str = "1900", when: datetime | None = None) -> Tick:
    return Tick(symbol=_XAU, price=Price(Decimal(price)), timestamp=when or _NOW)


class TestConnectDisconnect:
    async def test_connect_publishes_event_and_connects_provider(self) -> None:
        service = _make_service()
        received: list[object] = []

        async def handler(event: object) -> None:
            received.append(event)

        await service.event_bus.subscribe(EventType.PROVIDER_CONNECTED, handler)
        await service.connect()
        assert await service.provider.is_connected()
        assert len(received) == 1
        assert isinstance(received[0], ProviderConnected)

    async def test_disconnect_publishes_event(self) -> None:
        service = _make_service()
        await service.connect()
        received: list[object] = []

        async def handler(event: object) -> None:
            received.append(event)

        await service.event_bus.subscribe(EventType.PROVIDER_DISCONNECTED, handler)
        await service.disconnect(reason="test")
        assert not await service.provider.is_connected()
        assert len(received) == 1


class TestIngestTick:
    async def test_valid_tick_stored_cached_and_published(self) -> None:
        service = _make_service()
        received: list[object] = []

        async def handler(event: object) -> None:
            received.append(event)

        await service.event_bus.subscribe(EventType.MARKET_TICK_RECEIVED, handler)
        tick = _tick()
        await service.ingest_tick(tick)
        assert service.cache.get_latest_tick(_XAU) == tick
        assert await service.repository.ticks.get_latest(_XAU) == tick
        assert len(received) == 1

    async def test_duplicate_tick_rejected(self) -> None:
        service = _make_service()
        tick = _tick(when=_NOW)
        await service.ingest_tick(tick)
        with pytest.raises(ValidationError):
            await service.ingest_tick(_tick(when=_NOW))

    async def test_future_tick_rejected(self) -> None:
        service = _make_service()
        future_tick = _tick(when=_NOW + timedelta(hours=1))
        with pytest.raises(ValidationError):
            await service.ingest_tick(future_tick)


class TestIngestQuote:
    async def test_valid_quote_stored_cached_and_published(self) -> None:
        service = _make_service()
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
        )
        await service.ingest_quote(quote)
        assert service.cache.get_latest_quote(_XAU) == quote
        assert await service.repository.quotes.get_latest(_XAU) == quote

    async def test_future_quote_rejected(self) -> None:
        service = _make_service()
        quote = Quote(
            symbol=_XAU,
            bid=Price(Decimal("1900")),
            ask=Price(Decimal("1900.5")),
            timestamp=_NOW + timedelta(hours=1),
        )
        with pytest.raises(ValidationError):
            await service.ingest_quote(quote)


class TestIngestCandle:
    async def test_candle_stored_cached_and_published(self) -> None:
        service = _make_service()
        candle = OHLCVCandle(
            symbol=_XAU,
            timeframe=TimeFrame.M1,
            open=Price(Decimal("1900")),
            high=Price(Decimal("1901")),
            low=Price(Decimal("1899")),
            close=Price(Decimal("1900.5")),
            volume=Quantity(Decimal("10")),
            open_time=_NOW,
            close_time=_NOW + timedelta(minutes=1),
        )
        await service.ingest_candle(candle)
        assert service.cache.get_latest_candle(_XAU, TimeFrame.M1) == candle
        assert await service.repository.candles.get_latest(_XAU, TimeFrame.M1) == candle


class TestGetLatestPrice:
    async def test_prefers_cache(self) -> None:
        service = _make_service()
        tick = _tick()
        await service.ingest_tick(tick)
        result = await service.get_latest_price(_XAU)
        assert result == tick

    async def test_falls_back_to_repository_and_repopulates_cache(self) -> None:
        service = _make_service()
        tick = _tick()
        await service.repository.ticks.save(tick)
        result = await service.get_latest_price(_XAU)
        assert result == tick
        assert service.cache.get_latest_tick(_XAU) == tick

    async def test_returns_none_when_unknown(self) -> None:
        service = _make_service()
        assert await service.get_latest_price(_XAU) is None


class TestGetLatestQuote:
    async def test_prefers_cache(self) -> None:
        service = _make_service()
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
        )
        await service.ingest_quote(quote)
        assert await service.get_latest_quote(_XAU) == quote

    async def test_returns_none_when_unknown(self) -> None:
        service = _make_service()
        assert await service.get_latest_quote(_XAU) is None


class TestGetHistoricalCandles:
    async def test_fetches_stores_caches_and_publishes(self) -> None:
        service = _make_service()
        await service.connect()
        end = _NOW
        start = end - timedelta(minutes=5)
        candles = await service.get_historical_candles(_XAU, TimeFrame.M1, start=start, end=end)
        assert len(candles) > 0
        assert service.cache.get_last_n_candles(_XAU, TimeFrame.M1, 100) == candles

    async def test_unsupported_provider_raises(self) -> None:
        class BareProvider:
            async def connect(self) -> None: ...
            async def disconnect(self) -> None: ...
            async def is_connected(self) -> bool:
                return True

        service = MarketService(
            BareProvider(), InMemoryMarketRepository(), MarketCache(), AsyncEventBus()
        )
        with pytest.raises(InfrastructureError):
            await service.get_historical_candles(_XAU, TimeFrame.M1, start=_NOW, end=_NOW)


class TestFetchAndIngestQuote:
    async def test_fetches_and_ingests(self) -> None:
        service = _make_service()
        await service.connect()
        quote = await service.fetch_and_ingest_quote(_XAU)
        assert service.cache.get_latest_quote(_XAU) == quote

    async def test_unsupported_provider_raises(self) -> None:
        class BareProvider:
            async def connect(self) -> None: ...
            async def disconnect(self) -> None: ...
            async def is_connected(self) -> bool:
                return True

        service = MarketService(
            BareProvider(), InMemoryMarketRepository(), MarketCache(), AsyncEventBus()
        )
        with pytest.raises(InfrastructureError):
            await service.fetch_and_ingest_quote(_XAU)
