"""Structural conformance tests for the market data interfaces.

These interfaces have no implementation yet (per Milestone 3 scope), so
tests here verify only that the Protocols are well-formed and correctly
detect structural conformance — not any concrete behavior.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from quant_os.core.types import Price
from quant_os.events.domain_events import MarketTickReceived
from quant_os.events.metadata import EventMetadata
from quant_os.market.provider import MarketDataProvider
from quant_os.market.repository import MarketRepository


def _make_tick(symbol: str = "XAUUSD") -> MarketTickReceived:
    return MarketTickReceived(
        metadata=EventMetadata(source="test"),
        symbol=symbol,
        price=Price(Decimal("1900.00")),
        tick_time=datetime.now(UTC),
    )


class _ConformingProvider:
    """A minimal object satisfying the MarketDataProvider protocol."""

    async def get_latest_tick(self, symbol: str) -> MarketTickReceived:
        return _make_tick(symbol)

    async def stream_ticks(self, symbol: str) -> AsyncIterator[MarketTickReceived]:
        yield _make_tick(symbol)


class _NonConformingProvider:
    """An object missing required protocol methods."""


class _ConformingRepository:
    """A minimal object satisfying the MarketRepository protocol."""

    async def save(self, tick: MarketTickReceived) -> None:
        return None

    async def get_latest(self, symbol: str) -> MarketTickReceived | None:
        return None

    async def list_by_symbol(self, symbol: str, limit: int = 100) -> list[MarketTickReceived]:
        return []

    async def delete(self, tick_id: UUID) -> None:
        return None


class _NonConformingRepository:
    """An object missing required protocol methods."""


def test_conforming_provider_satisfies_protocol() -> None:
    assert isinstance(_ConformingProvider(), MarketDataProvider)


def test_non_conforming_provider_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingProvider(), MarketDataProvider)


def test_conforming_repository_satisfies_protocol() -> None:
    assert isinstance(_ConformingRepository(), MarketRepository)


def test_non_conforming_repository_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingRepository(), MarketRepository)
