"""Price precision: decimal places and minimum tick size for an instrument."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class PricePrecision(BaseModel):
    """The precision rules governing how an instrument's prices are quoted.

    Attributes:
        decimal_places: Number of decimal places prices are quoted to.
            Must be non-negative.
        tick_size: The minimum price increment. Must be strictly positive.
    """

    model_config = ConfigDict(frozen=True)

    decimal_places: int
    tick_size: Decimal

    @field_validator("decimal_places")
    @classmethod
    def _validate_decimal_places(cls, value: int) -> int:
        """Ensure decimal_places is non-negative."""
        if value < 0:
            raise ValueError("decimal_places must be >= 0")
        return value

    @field_validator("tick_size")
    @classmethod
    def _validate_tick_size(cls, value: Decimal) -> Decimal:
        """Ensure tick_size is strictly positive."""
        if value <= 0:
            raise ValueError("tick_size must be > 0")
        return value
