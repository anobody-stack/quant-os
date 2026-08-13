"""Market metadata: current status snapshot for an asset's market."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from quant_os.core.time import utc_now, validate_timezone_aware
from quant_os.market.models.asset import Asset
from quant_os.market.models.market_status import MarketStatus


class MarketMetadata(BaseModel):
    """A point-in-time snapshot of an asset's market status.

    Attributes:
        asset: The asset this metadata describes.
        status: The market's current trading status.
        last_updated: UTC time this snapshot was produced.
    """

    model_config = ConfigDict(frozen=True)

    asset: Asset
    status: MarketStatus
    last_updated: datetime = Field(default_factory=utc_now)

    @field_validator("last_updated")
    @classmethod
    def _validate_last_updated(cls, value: datetime) -> datetime:
        """Ensure last_updated is timezone-aware."""
        return validate_timezone_aware(value)
