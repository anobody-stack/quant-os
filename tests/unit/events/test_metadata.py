"""Unit tests for EventMetadata."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from quant_os.core.exceptions import ValidationError
from quant_os.events.enums import EventPriority
from quant_os.events.metadata import EventMetadata


def test_defaults() -> None:
    metadata = EventMetadata(source="test.provider")
    assert metadata.source == "test.provider"
    assert metadata.priority == EventPriority.NORMAL
    assert metadata.correlation_id is None
    assert metadata.timestamp.tzinfo is not None


def test_explicit_values() -> None:
    correlation_id = uuid4()
    event_id = uuid4()
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    metadata = EventMetadata(
        event_id=event_id,
        timestamp=timestamp,
        source="test",
        priority=EventPriority.CRITICAL,
        correlation_id=correlation_id,
    )
    assert metadata.event_id == event_id
    assert metadata.timestamp == timestamp
    assert metadata.priority == EventPriority.CRITICAL
    assert metadata.correlation_id == correlation_id


def test_naive_timestamp_rejected() -> None:
    with pytest.raises(ValidationError):
        EventMetadata(source="test", timestamp=datetime(2024, 1, 1))


def test_blank_source_rejected() -> None:
    with pytest.raises(PydanticValidationError):
        EventMetadata(source="   ")


def test_is_immutable() -> None:
    metadata = EventMetadata(source="test")
    with pytest.raises(PydanticValidationError):
        metadata.source = "changed"  # type: ignore[misc]
