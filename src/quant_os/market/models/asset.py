"""Asset model: a tradable instrument."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from quant_os.market.models.market import Market
from quant_os.market.models.precision import PricePrecision
from quant_os.market.models.symbol import AssetClass, Symbol


class Asset(BaseModel):
    """A tradable instrument.

    Attributes:
        symbol: The instrument's standardized symbol.
        name: A human-readable name (e.g. ``"Gold Spot"``).
        asset_class: The broad category this asset belongs to.
        quote_currency: The 3-letter currency the asset is quoted in.
        precision: This asset's price precision rules.
        market: The market this asset trades on.
    """

    model_config = ConfigDict(frozen=True)

    symbol: Symbol
    name: str
    asset_class: AssetClass
    quote_currency: str
    precision: PricePrecision
    market: Market

    @field_validator("quote_currency")
    @classmethod
    def _validate_currency(cls, value: str) -> str:
        """Ensure the quote currency is a 3-letter uppercase code."""
        if len(value) != 3 or not value.isalpha() or not value.isupper():
            raise ValueError("quote_currency must be a 3-letter uppercase code")
        return value
