"""Unit tests for Symbol, AssetClass, TimeFrame, and PricePrecision."""

from decimal import Decimal

import pytest
from pydantic import ValidationError as PydanticValidationError

from quant_os.market.models.precision import PricePrecision
from quant_os.market.models.symbol import AssetClass, Symbol
from quant_os.market.models.timeframe import TimeFrame


class TestSymbol:
    def test_valid_symbol(self) -> None:
        assert Symbol(code="XAUUSD").code == "XAUUSD"

    def test_too_short_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            Symbol(code="AB")

    def test_lowercase_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            Symbol(code="xauusd")

    def test_str(self) -> None:
        assert str(Symbol(code="EURUSD")) == "EURUSD"

    def test_hashable_and_usable_as_dict_key(self) -> None:
        d = {Symbol(code="XAUUSD"): 1}
        assert d[Symbol(code="XAUUSD")] == 1

    def test_equality(self) -> None:
        assert Symbol(code="XAUUSD") == Symbol(code="XAUUSD")


class TestAssetClass:
    def test_members(self) -> None:
        assert AssetClass.METAL == "metal"
        assert AssetClass.ENERGY == "energy"
        assert AssetClass.FX == "fx"


class TestTimeFrame:
    def test_tick_has_no_fixed_duration(self) -> None:
        assert TimeFrame.TICK.seconds is None

    def test_monthly_has_no_fixed_duration(self) -> None:
        assert TimeFrame.MN1.seconds is None

    def test_m1_is_60_seconds(self) -> None:
        assert TimeFrame.M1.seconds == 60

    def test_h4_is_correct(self) -> None:
        assert TimeFrame.H4.seconds == 4 * 60 * 60

    def test_all_members_present(self) -> None:
        expected = {"tick", "1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"}
        assert {member.value for member in TimeFrame} == expected


class TestPricePrecision:
    def test_valid(self) -> None:
        precision = PricePrecision(decimal_places=2, tick_size=Decimal("0.01"))
        assert precision.decimal_places == 2

    def test_negative_decimal_places_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            PricePrecision(decimal_places=-1, tick_size=Decimal("0.01"))

    def test_zero_tick_size_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            PricePrecision(decimal_places=2, tick_size=Decimal("0"))

    def test_negative_tick_size_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            PricePrecision(decimal_places=2, tick_size=Decimal("-0.01"))
