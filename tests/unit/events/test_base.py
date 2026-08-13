"""Unit tests for the abstract base Event class."""

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.events.base import Event
from quant_os.events.domain_events import RiskAlert
from quant_os.events.enums import EventPriority, EventType
from quant_os.events.metadata import EventMetadata


def test_base_event_cannot_be_instantiated_directly() -> None:
    metadata = EventMetadata(source="test")
    with pytest.raises(ValidationError):
        Event(metadata=metadata, event_type=EventType.NEWS_RECEIVED)


def test_concrete_subclass_can_be_instantiated() -> None:
    metadata = EventMetadata(source="test")
    alert = RiskAlert(
        metadata=metadata,
        message="drawdown exceeded",
        severity=EventPriority.HIGH,
    )
    assert isinstance(alert, Event)
    assert alert.event_type == EventType.RISK_ALERT
