"""Unit tests for MockMarketDataProvider."""

from datetime import UTC, datetime, timedelta

import pytest

from quant_os.core.exceptions import InfrastructureError
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.timeframe import TimeFrame
from quant_os.market.providers.mock_provider import MockMarketDataProvider

_XAU = Symbol(code="XAUUSD")
_UNSUPPORTED = Symbol(code="ZZZUSD")


class TestConnectionLifecycle:
    async def test_starts_disconnected(self) -> None:
        provider = MockMarketDataProvider()
        assert not await provider.is_connected()

    async def test_connect(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        assert await provider.is_connected()

    async def test_disconnect(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        await provider.disconnect()
        assert not await provider.is_connected()


class TestRequiresConnection:
    async def test_get_quote_requires_connection(self) -> None:
        provider = MockMarketDataProvider()
        with pytest.raises(InfrastructureError):
            await provider.get_quote(_XAU)

    async def test_get_market_status_requires_connection(self) -> None:
        provider = MockMarketDataProvider()
        with pytest.raises(InfrastructureError):
            await provider.get_market_status(_XAU)


class TestUnsupportedSymbol:
    async def test_get_quote_unsupported_symbol_raises(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        with pytest.raises(InfrastructureError):
            await provider.get_quote(_UNSUPPORTED)


class TestGetQuote:
    async def test_bid_less_than_or_equal_ask(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        quote = await provider.get_quote(_XAU)
        assert quote.bid.value <= quote.ask.value

    async def test_quote_symbol_matches(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        quote = await provider.get_quote(_XAU)
        assert quote.symbol == _XAU


class TestStreamTicks:
    async def test_yields_ticks_for_symbol(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        count = 0
        async for tick in provider.stream_ticks(_XAU):
            assert tick.symbol == _XAU
            count += 1
            if count >= 3:
                break
        assert count == 3


class TestGetCandles:
    async def test_returns_candles_covering_range(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        end = datetime.now(UTC)
        start = end - timedelta(minutes=5)
        candles = await provider.get_candles(_XAU, TimeFrame.M1, start=start, end=end)
        assert len(candles) >= 5
        assert candles[0].open_time <= candles[-1].open_time

    async def test_tick_timeframe_raises(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        end = datetime.now(UTC)
        with pytest.raises(InfrastructureError):
            await provider.get_candles(_XAU, TimeFrame.TICK, start=end, end=end)

    async def test_end_before_start_raises(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        end = datetime.now(UTC)
        start = end - timedelta(minutes=1)
        with pytest.raises(InfrastructureError):
            await provider.get_candles(_XAU, TimeFrame.M1, start=end, end=start)


class TestGetMarketMetadata:
    async def test_returns_metadata_for_symbol(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        metadata = await provider.get_market_metadata(_XAU)
        assert metadata.asset.symbol == _XAU


class TestGetMarketStatus:
    async def test_returns_open_while_connected(self) -> None:
        provider = MockMarketDataProvider()
        await provider.connect()
        status = await provider.get_market_status(_XAU)
        assert status == MarketStatus.OPEN


class TestDeterminism:
    async def test_same_seed_produces_same_sequence(self) -> None:
        provider_a = MockMarketDataProvider(seed=1)
        provider_b = MockMarketDataProvider(seed=1)
        await provider_a.connect()
        await provider_b.connect()
        quote_a = await provider_a.get_quote(_XAU)
        quote_b = await provider_b.get_quote(_XAU)
        assert quote_a.bid.value == quote_b.bid.value
