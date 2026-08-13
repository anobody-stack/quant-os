"""Symbol and asset classification."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,12}$")


class AssetClass(StrEnum):
    """The broad category an asset belongs to.

    Extensible: adding a new asset class is a one-line enum addition, not
    a structural change.
    """

    METAL = "metal"
    ENERGY = "energy"
    FX = "fx"


class Symbol(BaseModel):
    """A standardized instrument symbol (e.g. ``"XAUUSD"``).

    Attributes:
        code: The symbol code, uppercase alphanumeric, 3-12 characters.
    """

    model_config = ConfigDict(frozen=True)

    code: str

    @field_validator("code")
    @classmethod
    def _validate_code(cls, value: str) -> str:
        """Validate the symbol code's format.

        Args:
            value: The candidate symbol code.

        Returns:
            The validated code.

        Raises:
            ValueError: If ``value`` is not 3-12 uppercase alphanumeric
                characters.
        """
        if not _SYMBOL_PATTERN.match(value):
            raise ValueError("symbol code must be 3-12 uppercase alphanumeric characters")
        return value

    def __str__(self) -> str:
        """Return the symbol code."""
        return self.code

    def __hash__(self) -> int:
        """Hash by code, so Symbol can be used as a dict/set key."""
        return hash(self.code)
