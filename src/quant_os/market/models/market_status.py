"""Market status vocabulary."""

from __future__ import annotations

from enum import StrEnum


class MarketStatus(StrEnum):
    """The current trading status of a market."""

    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    POST_MARKET = "post_market"
    HALTED = "halted"
    UNKNOWN = "unknown"
