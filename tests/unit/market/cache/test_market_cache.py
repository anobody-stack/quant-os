"""Unit tests for MarketCache."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from quant_os.core.types import Price, Quantity
from quant_os.market.assets import get_supported_asset
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame

_XAU = Symbol(code="XAUUSD")
_NOW = datetime.now(UTC)


def _tick() -> Tick:
    return Tick(symbol=_XAU, price=Price(Decimal("1900")), timestamp=_NOW)


def _quote() -> Quote:
    return Quote(
        symbol=_XAU, bid=Price(Decimal("1900")), ask=Price(Decimal("1900.5")), timestamp=_NOW
    )


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


class TestLatestTick:
    def test_set_and_get(self) -> None:
        cache = MarketCache()
        tick = _tick()
        cache.set_latest_tick(tick)
        assert cache.get_latest_tick(_XAU) == tick

    def test_miss_returns_none(self) -> None:
        cache = MarketCache()
        assert cache.get_latest_tick(_XAU) is None

    def test_expired_entry_returns_none(self) -> None:
        cache = MarketCache(ttl=timedelta(seconds=-1))
        cache.set_latest_tick(_tick())
        assert cache.get_latest_tick(_XAU) is None


class TestLatestQuote:
    def test_set_and_get(self) -> None:
        cache = MarketCache()
        quote = _quote()
        cache.set_latest_quote(quote)
        assert cache.get_latest_quote(_XAU) == quote

    def test_miss_returns_none(self) -> None:
        cache = MarketCache()
        assert cache.get_latest_quote(_XAU) is None


class TestCandles:
    def test_set_and_get_latest(self) -> None:
        cache = MarketCache()
        candles = [_candle(_NOW), _candle(_NOW + timedelta(minutes=1))]
        cache.set_candles(_XAU, TimeFrame.M1, candles)
        assert cache.get_latest_candle(_XAU, TimeFrame.M1) == candles[-1]

    def test_get_latest_candle_miss_returns_none(self) -> None:
        cache = MarketCache()
        assert cache.get_latest_candle(_XAU, TimeFrame.M1) is None

    def test_get_last_n_candles(self) -> None:
        cache = MarketCache()
        candles = [_candle(_NOW + timedelta(minutes=i)) for i in range(5)]
        cache.set_candles(_XAU, TimeFrame.M1, candles)
        assert cache.get_last_n_candles(_XAU, TimeFrame.M1, 2) == candles[-2:]

    def test_get_last_n_candles_miss_returns_empty(self) -> None:
        cache = MarketCache()
        assert cache.get_last_n_candles(_XAU, TimeFrame.M1, 2) == []

    def test_history_is_trimmed(self) -> None:
        cache = MarketCache(candle_history=3)
        candles = [_candle(_NOW + timedelta(minutes=i)) for i in range(10)]
        cache.set_candles(_XAU, TimeFrame.M1, candles)
        assert cache.get_last_n_candles(_XAU, TimeFrame.M1, 100) == candles[-3:]


class TestMetadata:
    def test_set_and_get(self) -> None:
        cache = MarketCache()
        metadata = MarketMetadata(asset=get_supported_asset(_XAU), status=MarketStatus.OPEN)
        cache.set_metadata(metadata)
        assert cache.get_metadata(_XAU) == metadata

    def test_miss_returns_none(self) -> None:
        cache = MarketCache()
        assert cache.get_metadata(_XAU) is None


class TestInvalidateAndClear:
    def test_invalidate_clears_only_that_symbol(self) -> None:
        cache = MarketCache()
        other = Symbol(code="EURUSD")
        cache.set_latest_tick(_tick())
        cache.set_latest_tick(Tick(symbol=other, price=Price(Decimal("1.1")), timestamp=_NOW))
        cache.invalidate(_XAU)
        assert cache.get_latest_tick(_XAU) is None
        assert cache.get_latest_tick(other) is not None

    def test_invalidate_clears_candles_for_symbol(self) -> None:
        cache = MarketCache()
        cache.set_candles(_XAU, TimeFrame.M1, [_candle(_NOW)])
        cache.invalidate(_XAU)
        assert cache.get_latest_candle(_XAU, TimeFrame.M1) is None

    def test_clear_removes_everything(self) -> None:
        cache = MarketCache()
        cache.set_latest_tick(_tick())
        cache.set_latest_quote(_quote())
        cache.set_candles(_XAU, TimeFrame.M1, [_candle(_NOW)])
        cache.clear()
        assert cache.get_latest_tick(_XAU) is None
        assert cache.get_latest_quote(_XAU) is None
        assert cache.get_latest_candle(_XAU, TimeFrame.M1) is None
