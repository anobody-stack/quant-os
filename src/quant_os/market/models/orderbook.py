"""Order book snapshot model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from quant_os.core.time import validate_timezone_aware
from quant_os.core.types import Price, Quantity
from quant_os.market.models.symbol import Symbol


class OrderBookLevel(BaseModel):
    """A single price level in an order book.

    Attributes:
        price: The price at this level.
        quantity: The total quantity available at this level.
    """

    model_config = ConfigDict(frozen=True)

    price: Price
    quantity: Quantity


class OrderBookSnapshot(BaseModel):
    """A point-in-time snapshot of an order book.

    Attributes:
        symbol: The instrument this snapshot belongs to.
        bids: Bid-side levels, conventionally best-first.
        asks: Ask-side levels, conventionally best-first.
        timestamp: UTC time the snapshot was taken.
    """

    model_config = ConfigDict(frozen=True)

    symbol: Symbol
    bids: tuple[OrderBookLevel, ...]
    asks: tuple[OrderBookLevel, ...]
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, value: datetime) -> datetime:
        """Ensure the timestamp is timezone-aware."""
        return validate_timezone_aware(value)
