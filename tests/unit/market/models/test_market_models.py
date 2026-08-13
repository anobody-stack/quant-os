"""Unit tests for Exchange, MarketSession, MarketStatus, Market, Asset, MarketMetadata."""

from decimal import Decimal

import pytest
from pydantic import ValidationError as PydanticValidationError

from quant_os.market.models.asset import Asset
from quant_os.market.models.exchange import Exchange
from quant_os.market.models.market import Market
from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.market_session import MarketSession
from quant_os.market.models.market_status import MarketStatus
from quant_os.market.models.precision import PricePrecision
from quant_os.market.models.symbol import AssetClass, Symbol


def _make_exchange() -> Exchange:
    return Exchange(code="COMEX", name="COMEX", timezone="America/New_York")


def _make_market() -> Market:
    session = MarketSession(name="regular", opens_at="00:00", closes_at="23:59")
    return Market(name="Gold", exchange=_make_exchange(), sessions=(session,))


def _make_asset() -> Asset:
    return Asset(
        symbol=Symbol(code="XAUUSD"),
        name="Gold Spot",
        asset_class=AssetClass.METAL,
        quote_currency="USD",
        precision=PricePrecision(decimal_places=2, tick_size=Decimal("0.01")),
        market=_make_market(),
    )


class TestExchange:
    def test_valid(self) -> None:
        exchange = _make_exchange()
        assert exchange.code == "COMEX"

    def test_blank_name_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            Exchange(code="COMEX", name="  ", timezone="UTC")


class TestMarketSession:
    def test_valid(self) -> None:
        session = MarketSession(name="regular", opens_at="09:30", closes_at="16:00")
        assert session.opens_at == "09:30"

    def test_invalid_time_format_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            MarketSession(name="regular", opens_at="9:30", closes_at="16:00")

    def test_out_of_range_hour_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            MarketSession(name="regular", opens_at="25:00", closes_at="16:00")


class TestMarketStatus:
    def test_members(self) -> None:
        expected = {"open", "closed", "pre_market", "post_market", "halted", "unknown"}
        assert {member.value for member in MarketStatus} == expected


class TestMarket:
    def test_valid(self) -> None:
        market = _make_market()
        assert market.name == "Gold"
        assert len(market.sessions) == 1

    def test_defaults_to_no_sessions(self) -> None:
        market = Market(name="Gold", exchange=_make_exchange())
        assert market.sessions == ()


class TestAsset:
    def test_valid(self) -> None:
        asset = _make_asset()
        assert asset.symbol.code == "XAUUSD"
        assert asset.quote_currency == "USD"

    def test_invalid_currency_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            Asset(
                symbol=Symbol(code="XAUUSD"),
                name="Gold Spot",
                asset_class=AssetClass.METAL,
                quote_currency="us",
                precision=PricePrecision(decimal_places=2, tick_size=Decimal("0.01")),
                market=_make_market(),
            )


class TestMarketMetadata:
    def test_valid(self) -> None:
        metadata = MarketMetadata(asset=_make_asset(), status=MarketStatus.OPEN)
        assert metadata.status == MarketStatus.OPEN
        assert metadata.last_updated.tzinfo is not None
