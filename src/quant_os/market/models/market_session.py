"""Market trading session model."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, field_validator

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class MarketSession(BaseModel):
    """A recurring trading session window.

    Attributes:
        name: A short label for the session (e.g. ``"regular"``).
        opens_at: Session open time, ``"HH:MM"`` 24-hour format, in the
            exchange's local timezone.
        closes_at: Session close time, ``"HH:MM"`` 24-hour format, in the
            exchange's local timezone.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    opens_at: str
    closes_at: str

    @field_validator("opens_at", "closes_at")
    @classmethod
    def _validate_time_format(cls, value: str) -> str:
        """Ensure the time string is HH:MM in 24-hour format."""
        if not _TIME_PATTERN.match(value):
            raise ValueError('time must be in "HH:MM" 24-hour format')
        return value
