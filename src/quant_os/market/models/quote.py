"""Quote model: a bid/ask price pair."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from quant_os.core.time import validate_timezone_aware
from quant_os.core.types import Price, Quantity
from quant_os.market.models.symbol import Symbol


class Quote(BaseModel):
    """A two-sided price quote for a symbol.

    Attributes:
        symbol: The instrument this quote belongs to.
        bid: The bid (buy) price.
        ask: The ask (sell) price.
        bid_size: The size available at the bid, if known.
        ask_size: The size available at the ask, if known.
        timestamp: UTC time the quote was observed.
    """

    model_config = ConfigDict(frozen=True)

    symbol: Symbol
    bid: Price
    ask: Price
    bid_size: Quantity | None = None
    ask_size: Quantity | None = None
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, value: datetime) -> datetime:
        """Ensure the timestamp is timezone-aware."""
        return validate_timezone_aware(value)

    @model_validator(mode="after")
    def _validate_spread(self) -> Quote:
        """Ensure the bid does not exceed the ask (a non-negative spread).

        Returns:
            This instance, unchanged, when valid.

        Raises:
            ValueError: If ``bid`` is greater than ``ask``.
        """
        if self.bid.value > self.ask.value:
            raise ValueError(f"bid ({self.bid.value}) must not exceed ask ({self.ask.value})")
        return self
