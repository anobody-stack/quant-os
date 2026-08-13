"""Structural conformance tests for the macro interfaces."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

from quant_os.events.domain_events import EconomicEventReceived
from quant_os.events.metadata import EventMetadata
from quant_os.macro.provider import MacroProvider
from quant_os.macro.repository import MacroRepository


def _make_event(name: str = "Non-Farm Payrolls") -> EconomicEventReceived:
    return EconomicEventReceived(
        metadata=EventMetadata(source="test"),
        name=name,
        country="United States",
        scheduled_at=datetime.now(UTC),
    )


class _ConformingProvider:
    async def get_upcoming_events(self, limit: int = 50) -> list[EconomicEventReceived]:
        return [_make_event()]

    async def stream(self) -> AsyncIterator[EconomicEventReceived]:
        yield _make_event()


class _NonConformingProvider:
    pass


class _ConformingRepository:
    async def save(self, event: EconomicEventReceived) -> None:
        return None

    async def get_by_id(self, economic_event_id: UUID) -> EconomicEventReceived | None:
        return None

    async def list_by_country(self, country: str, limit: int = 50) -> list[EconomicEventReceived]:
        return []

    async def delete(self, economic_event_id: UUID) -> None:
        return None


class _NonConformingRepository:
    pass


def test_conforming_provider_satisfies_protocol() -> None:
    assert isinstance(_ConformingProvider(), MacroProvider)


def test_non_conforming_provider_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingProvider(), MacroProvider)


def test_conforming_repository_satisfies_protocol() -> None:
    assert isinstance(_ConformingRepository(), MacroRepository)


def test_non_conforming_repository_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingRepository(), MacroRepository)
