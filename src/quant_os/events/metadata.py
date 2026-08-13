"""Event metadata: the envelope information common to every event."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from quant_os.core.time import utc_now, validate_timezone_aware
from quant_os.events.enums import EventPriority


class EventMetadata(BaseModel):
    """Envelope metadata attached to every event.

    Attributes:
        event_id: Unique identifier for this specific event instance.
        timestamp: UTC, timezone-aware time the event was created.
        source: Name of the subsystem or component that published the
            event (e.g. ``"news.reuters_provider"``).
        priority: Urgency of the event. Defaults to ``EventPriority.NORMAL``.
        correlation_id: Optional identifier linking this event to a
            broader causal chain (e.g. the request or workflow that
            triggered it).
    """

    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=utc_now)
    source: str
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: UUID | None = None

    @field_validator("timestamp")
    @classmethod
    def _timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Ensure the timestamp is UTC-aware, not naive.

        Args:
            value: The candidate timestamp.

        Returns:
            The validated, timezone-aware timestamp.

        Raises:
            quant_os.core.exceptions.ValidationError: If ``value`` is naive.
        """
        return validate_timezone_aware(value)

    @field_validator("source")
    @classmethod
    def _source_must_not_be_blank(cls, value: str) -> str:
        """Ensure the source identifier is non-empty.

        Args:
            value: The candidate source string.

        Returns:
            The validated source string.

        Raises:
            ValueError: If ``value`` is blank or whitespace-only.
        """
        if not value.strip():
            raise ValueError("source must not be blank")
        return value
