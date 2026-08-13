"""Unit tests for the supported assets registry."""

import pytest

from quant_os.core.exceptions import ValidationError
from quant_os.market.assets import SUPPORTED_ASSETS, get_supported_asset
from quant_os.market.models.symbol import Symbol


def test_four_assets_supported() -> None:
    assert set(SUPPORTED_ASSETS) == {"XAUUSD", "WTIUSD", "BCOUSD", "EURUSD"}


def test_get_supported_asset_returns_correct_asset() -> None:
    asset = get_supported_asset(Symbol(code="XAUUSD"))
    assert asset.name == "Gold Spot"


def test_get_supported_asset_unknown_symbol_raises() -> None:
    with pytest.raises(ValidationError):
        get_supported_asset(Symbol(code="UNKNOWN"))
