"""Macro/economic event repository interface.

This is an interface only — no storage backend (in-memory, database, etc.)
is implemented here. That is reserved for a later milestone.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from quant_os.events.domain_events import EconomicEventReceived


@runtime_checkable
class MacroRepository(Protocol):
    """Abstraction for persisting and retrieving economic events."""

    async def save(self, event: EconomicEventReceived) -> None:
        """Persist an economic event.

        Args:
            event: The event to persist.
        """
        ...

    async def get_by_id(self, economic_event_id: UUID) -> EconomicEventReceived | None:
        """Retrieve a stored economic event by identifier.

        Args:
            economic_event_id: Identifier of the event to look up.

        Returns:
            The stored event, or ``None`` if no event with that
            identifier exists.
        """
        ...

    async def list_by_country(self, country: str, limit: int = 50) -> list[EconomicEventReceived]:
        """List stored economic events for a country.

        Args:
            country: Standardized country identifier to filter by.
            limit: Maximum number of events to return.

        Returns:
            Stored events for ``country``, soonest-scheduled first.
        """
        ...

    async def delete(self, economic_event_id: UUID) -> None:
        """Delete a stored economic event by identifier.

        Args:
            economic_event_id: Identifier of the event to delete.
        """
        ...
