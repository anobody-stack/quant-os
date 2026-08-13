"""The registry of initially supported assets.

Only Gold, WTI Crude Oil, Brent Crude Oil, and EUR/USD are supported at
this milestone. Adding a future asset means adding one entry to
:data:`SUPPORTED_ASSETS` below — no structural change required.
"""

from __future__ import annotations

from decimal import Decimal

from quant_os.core.exceptions import ValidationError
from quant_os.market.models.asset import Asset
from quant_os.market.models.exchange import Exchange
from quant_os.market.models.market import Market
from quant_os.market.models.market_session import MarketSession
from quant_os.market.models.precision import PricePrecision
from quant_os.market.models.symbol import AssetClass, Symbol

_OTC = Exchange(code="OTC", name="Over-the-Counter", timezone="UTC")
_REGULAR_SESSION = MarketSession(name="regular", opens_at="00:00", closes_at="23:59")

_XAUUSD = Asset(
    symbol=Symbol(code="XAUUSD"),
    name="Gold Spot",
    asset_class=AssetClass.METAL,
    quote_currency="USD",
    precision=PricePrecision(decimal_places=2, tick_size=Decimal("0.01")),
    market=Market(name="Gold", exchange=_OTC, sessions=(_REGULAR_SESSION,)),
)

_WTIUSD = Asset(
    symbol=Symbol(code="WTIUSD"),
    name="WTI Crude Oil",
    asset_class=AssetClass.ENERGY,
    quote_currency="USD",
    precision=PricePrecision(decimal_places=2, tick_size=Decimal("0.01")),
    market=Market(name="WTI Crude Oil", exchange=_OTC, sessions=(_REGULAR_SESSION,)),
)

_BCOUSD = Asset(
    symbol=Symbol(code="BCOUSD"),
    name="Brent Crude Oil",
    asset_class=AssetClass.ENERGY,
    quote_currency="USD",
    precision=PricePrecision(decimal_places=2, tick_size=Decimal("0.01")),
    market=Market(name="Brent Crude Oil", exchange=_OTC, sessions=(_REGULAR_SESSION,)),
)

_EURUSD = Asset(
    symbol=Symbol(code="EURUSD"),
    name="Euro / US Dollar",
    asset_class=AssetClass.FX,
    quote_currency="USD",
    precision=PricePrecision(decimal_places=4, tick_size=Decimal("0.0001")),
    market=Market(name="EUR/USD", exchange=_OTC, sessions=(_REGULAR_SESSION,)),
)

SUPPORTED_ASSETS: dict[str, Asset] = {
    asset.symbol.code: asset for asset in (_XAUUSD, _WTIUSD, _BCOUSD, _EURUSD)
}
"""All initially supported assets, keyed by symbol code."""


def get_supported_asset(symbol: Symbol) -> Asset:
    """Look up a supported asset by symbol.

    Args:
        symbol: The symbol to look up.

    Returns:
        The matching :class:`~quant_os.market.models.asset.Asset`.

    Raises:
        ValidationError: If ``symbol`` is not one of the initially
            supported assets.
    """
    asset = SUPPORTED_ASSETS.get(symbol.code)
    if asset is None:
        raise ValidationError(
            f"Unsupported symbol: {symbol.code!r}", context={"symbol": symbol.code}
        )
    return asset
