"""Tick model: a single trade or price update."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from quant_os.core.time import validate_timezone_aware
from quant_os.core.types import Price, Quantity
from quant_os.market.models.symbol import Symbol


class Tick(BaseModel):
    """A single price observation for a symbol at a point in time.

    Attributes:
        symbol: The instrument this tick belongs to.
        price: The traded or quoted price.
        volume: The traded size, if known.
        timestamp: UTC time the tick occurred.
    """

    model_config = ConfigDict(frozen=True)

    symbol: Symbol
    price: Price
    volume: Quantity | None = None
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, value: datetime) -> datetime:
        """Ensure the timestamp is timezone-aware."""
        return validate_timezone_aware(value)
