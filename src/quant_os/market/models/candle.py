"""OHLCV candle model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from quant_os.core.time import validate_timezone_aware
from quant_os.core.types import Price, Quantity
from quant_os.market.models.symbol import Symbol
from quant_os.market.models.timeframe import TimeFrame


class OHLCVCandle(BaseModel):
    """An open/high/low/close/volume bar for a symbol over a timeframe.

    Attributes:
        symbol: The instrument this candle belongs to.
        timeframe: The bar's granularity.
        open: The opening price.
        high: The highest price during the bar.
        low: The lowest price during the bar.
        close: The closing price.
        volume: The total traded volume during the bar.
        open_time: UTC time the bar opened.
        close_time: UTC time the bar closed.
    """

    model_config = ConfigDict(frozen=True)

    symbol: Symbol
    timeframe: TimeFrame
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Quantity
    open_time: datetime
    close_time: datetime

    @field_validator("open_time", "close_time")
    @classmethod
    def _validate_timestamps(cls, value: datetime) -> datetime:
        """Ensure timestamps are timezone-aware."""
        return validate_timezone_aware(value)

    @model_validator(mode="after")
    def _validate_ohlc_consistency(self) -> OHLCVCandle:
        """Ensure OHLC values and bar timing are internally consistent.

        Returns:
            This instance, unchanged, when valid.

        Raises:
            ValueError: If ``low`` exceeds any of ``open``/``high``/
                ``close``, if ``high`` is less than any of them, or if
                ``close_time`` precedes ``open_time``.
        """
        low, high = self.low.value, self.high.value
        if low > high:
            raise ValueError(f"low ({low}) must not exceed high ({high})")
        for name, price in (("open", self.open), ("close", self.close)):
            if not (low <= price.value <= high):
                raise ValueError(f"{name} ({price.value}) must be within [low={low}, high={high}]")
        if self.close_time < self.open_time:
            raise ValueError("close_time must not precede open_time")
        return self
