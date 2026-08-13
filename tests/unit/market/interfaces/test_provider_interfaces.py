"""Structural conformance tests for provider interfaces."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from quant_os.market.interfaces.providers import (
    HistoricalDataProvider,
    MarketDataProvider,
    MetadataProvider,
    QuoteProvider,
    StreamingProvider,
)
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame


class _ConformingMarketDataProvider:
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def is_connected(self) -> bool:
        return True


class _ConformingHistoricalProvider:
    async def get_candles(
        self, symbol: Symbol, timeframe: TimeFrame, *, start: datetime, end: datetime
    ) -> list[OHLCVCandle]:
        return []


class _ConformingStreamingProvider:
    async def stream_ticks(self, symbol: Symbol) -> AsyncIterator[Tick]:
        return
        yield  # pragma: no cover - makes this an async generator


class _ConformingQuoteProvider:
    async def get_quote(self, symbol: Symbol) -> Quote:
        raise NotImplementedError


class _ConformingMetadataProvider:
    async def get_market_metadata(self, symbol: Symbol) -> MarketMetadata:
        raise NotImplementedError

    async def get_market_status(self, symbol: Symbol) -> MarketStatus:
        return MarketStatus.OPEN


class _NonConforming:
    pass


def test_market_data_provider_conformance() -> None:
    assert isinstance(_ConformingMarketDataProvider(), MarketDataProvider)
    assert not isinstance(_NonConforming(), MarketDataProvider)


def test_historical_data_provider_conformance() -> None:
    assert isinstance(_ConformingHistoricalProvider(), HistoricalDataProvider)
    assert not isinstance(_NonConforming(), HistoricalDataProvider)


def test_streaming_provider_conformance() -> None:
    assert isinstance(_ConformingStreamingProvider(), StreamingProvider)
    assert not isinstance(_NonConforming(), StreamingProvider)


def test_quote_provider_conformance() -> None:
    assert isinstance(_ConformingQuoteProvider(), QuoteProvider)
    assert not isinstance(_NonConforming(), QuoteProvider)


def test_metadata_provider_conformance() -> None:
    assert isinstance(_ConformingMetadataProvider(), MetadataProvider)
    assert not isinstance(_NonConforming(), MetadataProvider)
