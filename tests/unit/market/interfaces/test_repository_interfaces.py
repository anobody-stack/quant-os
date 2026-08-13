"""Structural conformance tests for repository interfaces."""

from __future__ import annotations

from datetime import datetime

from quant_os.market.interfaces.repositories import (
    CandleRepository,
    MetadataRepository,
    QuoteRepository,
    TickRepository,
)
from quant_os.market.models.candle import OHLCVCandle
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.quote import Quote
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.tick import Tick
from quant_os.market.models.timeframe import TimeFrame


class _ConformingTickRepository:
    async def save(self, tick: Tick) -> None: ...
    async def get_latest(self, symbol: Symbol) -> Tick | None:
        return None

    async def list_recent(self, symbol: Symbol, limit: int = 100) -> list[Tick]:
        return []


class _ConformingQuoteRepository:
    async def save(self, quote: Quote) -> None: ...
    async def get_latest(self, symbol: Symbol) -> Quote | None:
        return None


class _ConformingCandleRepository:
    async def save(self, candle: OHLCVCandle) -> None: ...
    async def get_latest(self, symbol: Symbol, timeframe: TimeFrame) -> OHLCVCandle | None:
        return None

    async def get_last_n(self, symbol: Symbol, timeframe: TimeFrame, n: int) -> list[OHLCVCandle]:
        return []

    async def get_range(
        self, symbol: Symbol, timeframe: TimeFrame, *, start: datetime, end: datetime
    ) -> list[OHLCVCandle]:
        return []


class _ConformingMetadataRepository:
    async def save(self, metadata: MarketMetadata) -> None: ...
    async def get(self, symbol: Symbol) -> MarketMetadata | None:
        return None


class _NonConforming:
    pass


def test_tick_repository_conformance() -> None:
    assert isinstance(_ConformingTickRepository(), TickRepository)
    assert not isinstance(_NonConforming(), TickRepository)


def test_quote_repository_conformance() -> None:
    assert isinstance(_ConformingQuoteRepository(), QuoteRepository)
    assert not isinstance(_NonConforming(), QuoteRepository)


def test_candle_repository_conformance() -> None:
    assert isinstance(_ConformingCandleRepository(), CandleRepository)
    assert not isinstance(_NonConforming(), CandleRepository)


def test_metadata_repository_conformance() -> None:
    assert isinstance(_ConformingMetadataRepository(), MetadataRepository)
    assert not isinstance(_NonConforming(), MetadataRepository)
