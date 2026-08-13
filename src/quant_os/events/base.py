"""The abstract base event all domain events derive from."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator

from quant_os.core.exceptions import ValidationError
from quant_os.events.enums import EventType
from quant_os.events.metadata import EventMetadata


class Event(BaseModel):
    """Abstract base class for every event published on the event bus.

    Concrete events (see :mod:`quant_os.events.domain_events`) subclass
    this and override :attr:`event_type` with their specific
    :class:`~quant_os.events.enums.EventType`. Instances of ``Event``
    itself cannot be constructed.

    Attributes:
        metadata: Envelope information common to all events.
        event_type: The specific kind of event this instance represents.
    """

    model_config = ConfigDict(frozen=True)

    metadata: EventMetadata
    event_type: EventType

    @model_validator(mode="after")
    def _forbid_direct_instantiation(self) -> Event:
        """Prevent the abstract base class from being instantiated directly.

        Returns:
            This instance, unchanged, when the check passes.

        Raises:
            quant_os.core.exceptions.ValidationError: If this instance is
                exactly an ``Event`` rather than a subclass.
        """
        if type(self) is Event:
            raise ValidationError(
                "Event is abstract and cannot be instantiated directly; "
                "use a concrete subclass from quant_os.events.domain_events"
            )
        return self
