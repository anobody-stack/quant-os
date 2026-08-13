"""Unit tests for in-memory repository implementations."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from quant_os.core.types import Price, Quantity
from quant_os.market.assets import get_supported_asset
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame
from quant_os.market.repositories.candle_repository import InMemoryCandleRepository
from quant_os.market.repositories.market_repository import InMemoryMarketRepository
from quant_os.market.repositories.metadata_repository import InMemoryMetadataRepository
from quant_os.market.repositories.quote_repository import InMemoryQuoteRepository
from quant_os.market.repositories.tick_repository import InMemoryTickRepository

_XAU = Symbol(code="XAUUSD")
_NOW = datetime.now(UTC)


def _tick(price: str = "1900", when: datetime | None = None) -> Tick:
    return Tick(symbol=_XAU, price=Price(Decimal(price)), timestamp=when or _NOW)


def _candle(open_time: datetime) -> OHLCVCandle:
    return OHLCVCandle(
        symbol=_XAU,
        timeframe=TimeFrame.M1,
        open=Price(Decimal("1900")),
        high=Price(Decimal("1901")),
        low=Price(Decimal("1899")),
        close=Price(Decimal("1900.5")),
        volume=Quantity(Decimal("10")),
        open_time=open_time,
        close_time=open_time + timedelta(minutes=1),
    )


class TestInMemoryTickRepository:
    async def test_save_and_get_latest(self) -> None:
        repo = InMemoryTickRepository()
        tick = _tick()
        await repo.save(tick)
        assert await repo.get_latest(_XAU) == tick

    async def test_get_latest_unknown_symbol_returns_none(self) -> None:
        repo = InMemoryTickRepository()
        assert await repo.get_latest(_XAU) is None

    async def test_list_recent_most_recent_first(self) -> None:
        repo = InMemoryTickRepository()
        first = _tick(price="1900", when=_NOW)
        second = _tick(price="1901", when=_NOW + timedelta(seconds=1))
        await repo.save(first)
        await repo.save(second)
        recent = await repo.list_recent(_XAU)
        assert recent == [second, first]

    async def test_list_recent_respects_limit(self) -> None:
        repo = InMemoryTickRepository()
        for i in range(5):
            await repo.save(_tick(price="1900", when=_NOW + timedelta(seconds=i)))
        assert len(await repo.list_recent(_XAU, limit=2)) == 2


class TestInMemoryQuoteRepository:
    async def test_save_and_get_latest(self) -> None:
        repo = InMemoryQuoteRepository()
        quote = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
        )
        await repo.save(quote)
        assert await repo.get_latest(_XAU) == quote

    async def test_get_latest_unknown_symbol_returns_none(self) -> None:
        repo = InMemoryQuoteRepository()
        assert await repo.get_latest(_XAU) is None

    async def test_save_replaces_previous(self) -> None:
        repo = InMemoryQuoteRepository()
        first = Quote(
            symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
        )
        second = Quote(
            symbol=_XAU, bid=Price(Decimal("1901")), ask=Price(Decimal("1901.5")), timestamp=_NOW
        )
        await repo.save(first)
        await repo.save(second)
        assert await repo.get_latest(_XAU) == second


class TestInMemoryCandleRepository:
    async def test_save_and_get_latest(self) -> None:
        repo = InMemoryCandleRepository()
        candle = _candle(_NOW)
        await repo.save(candle)
        assert await repo.get_latest(_XAU, TimeFrame.M1) == candle

    async def test_get_latest_unknown_returns_none(self) -> None:
        repo = InMemoryCandleRepository()
        assert await repo.get_latest(_XAU, TimeFrame.M1) is None

    async def test_get_last_n(self) -> None:
        repo = InMemoryCandleRepository()
        for i in range(5):
            await repo.save(_candle(_NOW + timedelta(minutes=i)))
        last_two = await repo.get_last_n(_XAU, TimeFrame.M1, 2)
        assert len(last_two) == 2
        assert last_two[0].open_time < last_two[1].open_time

    async def test_get_last_n_empty(self) -> None:
        repo = InMemoryCandleRepository()
        assert await repo.get_last_n(_XAU, TimeFrame.M1, 5) == []

    async def test_get_range(self) -> None:
        repo = InMemoryCandleRepository()
        for i in range(5):
            await repo.save(_candle(_NOW + timedelta(minutes=i)))
        result = await repo.get_range(
            _XAU, TimeFrame.M1, start=_NOW + timedelta(minutes=1), end=_NOW + timedelta(minutes=2)
        )
        assert len(result) == 2

    async def test_get_range_empty_series(self) -> None:
        repo = InMemoryCandleRepository()
        result = await repo.get_range(_XAU, TimeFrame.M1, start=_NOW, end=_NOW)
        assert result == []


class TestInMemoryMetadataRepository:
    async def test_save_and_get(self) -> None:
        repo = InMemoryMetadataRepository()
        metadata = MarketMetadata(asset=get_supported_asset(_XAU), status=MarketStatus.OPEN)
        await repo.save(metadata)
        assert await repo.get(_XAU) == metadata

    async def test_get_unknown_returns_none(self) -> None:
        repo = InMemoryMetadataRepository()
        assert await repo.get(_XAU) is None


class TestInMemoryMarketRepository:
    async def test_default_construction_creates_all_sub_repositories(self) -> None:
        repo = InMemoryMarketRepository()
        tick = _tick()
        await repo.ticks.save(tick)
        assert await repo.ticks.get_latest(_XAU) == tick

    async def test_can_be_constructed_with_explicit_sub_repositories(self) -> None:
        ticks = InMemoryTickRepository()
        repo = InMemoryMarketRepository(ticks=ticks)
        assert repo.ticks is ticks
