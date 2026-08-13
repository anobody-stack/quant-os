"""Exchange model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class Exchange(BaseModel):
    """A venue an asset trades on.

    Attributes:
        code: A short, unique identifier (e.g. ``"COMEX"``, ``"OTC"``).
        name: The exchange's full name.
        timezone: The exchange's IANA timezone name (e.g. ``"America/New_York"``).
    """

    model_config = ConfigDict(frozen=True)

    code: str
    name: str
    timezone: str

    @field_validator("code", "name", "timezone")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        """Ensure string fields are non-blank."""
        if not value.strip():
            raise ValueError("must not be blank")
        return value
