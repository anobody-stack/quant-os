"""Market model: an exchange plus its trading sessions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from quant_os.market.models.exchange import Exchange
from quant_os.market.models.market_session import MarketSession


class Market(BaseModel):
    """A market: an exchange and the sessions it trades in.

    Attributes:
        name: A short label for the market (e.g. ``"COMEX Gold"``).
        exchange: The exchange this market trades on.
        sessions: The recurring trading sessions for this market.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    exchange: Exchange
    sessions: tuple[MarketSession, ...] = Field(default_factory=tuple)
