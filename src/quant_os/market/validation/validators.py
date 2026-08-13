"""Validation for incoming market data.

These functions validate structural/domain invariants beyond what the
pydantic models themselves enforce (e.g. duplicate detection, future
timestamps), and are used by the Market Service before data is stored or
published.
"""

from __future__ import annotations

from datetime import datetime

from quant_os.core.exceptions import ValidationError
from quant_os.core.time import utc_now
from quant_os.core.types import Price
from quant_os.market.models.precision import PricePrecision
from quant_os.market.models.quote import Quote
from quant_os.market.models.tick import Tick


def validate_tick(tick: Tick, *, last_tick: Tick | None = None) -> Tick:
    """Validate a tick before it enters the Market Engine.

    Args:
        tick: The tick to validate.
        last_tick: The most recently accepted tick for the same symbol,
            if any, used for duplicate detection.

    Returns:
        The validated tick, unchanged.

    Raises:
        ValidationError: If the tick's timestamp is in the future, or if
            it is a duplicate of ``last_tick`` (same price and timestamp).
    """
    _reject_future_timestamp(tick.timestamp, field_name="timestamp")
    if (
        last_tick is not None
        and last_tick.timestamp == tick.timestamp
        and last_tick.price.value == tick.price.value
    ):
        raise ValidationError(
            "Duplicate tick: identical price and timestamp as the last accepted tick",
            context={
                "symbol": str(tick.symbol),
                "timestamp": tick.timestamp.isoformat(),
                "price": str(tick.price.value),
            },
        )
    return tick


def validate_quote(quote: Quote) -> Quote:
    """Validate a quote before it enters the Market Engine.

    The bid/ask ordering itself is already enforced by the
    :class:`~quant_os.market.models.quote.Quote` model; this additionally
    rejects future timestamps.

    Args:
        quote: The quote to validate.

    Returns:
        The validated quote, unchanged.

    Raises:
        ValidationError: If the quote's timestamp is in the future.
    """
    _reject_future_timestamp(quote.timestamp, field_name="timestamp")
    return quote


def validate_precision(price: Price, precision: PricePrecision) -> Price:
    """Validate that a price conforms to an asset's tick size.

    Args:
        price: The price to validate.
        precision: The precision rules to validate against.

    Returns:
        The validated price, unchanged.

    Raises:
        ValidationError: If ``price`` is not an integer multiple of
            ``precision.tick_size``.
    """
    remainder = price.value % precision.tick_size
    if remainder != 0:
        raise ValidationError(
            f"price {price.value} is not a multiple of tick size {precision.tick_size}",
            context={"price": str(price.value), "tick_size": str(precision.tick_size)},
        )
    return price


def _reject_future_timestamp(timestamp: datetime, *, field_name: str) -> None:
    """Raise if ``timestamp`` is later than the current UTC time.

    Args:
        timestamp: The timezone-aware timestamp to check.
        field_name: Name of the field being validated, used in the error
            message.

    Raises:
        ValidationError: If ``timestamp`` is in the future.
    """
    now = utc_now()
    if timestamp > now:
        raise ValidationError(
            f"{field_name} must not be in the future",
            context={"field_name": field_name, "value": str(timestamp), "now": now.isoformat()},
        )
