"""Unit tests for MarketModule (Kernel integration)."""

from quant_os.events import AsyncEventBus
from quant_os.kernel.capabilities import Capability
from quant_os.kernel.health import HealthStatus
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.providers.mock_provider import MockMarketDataProvider
from quant_os.market.repositories.market_repository import InMemoryMarketRepository
from quant_os.market.services.market_module import MarketModule


def _make_module() -> MarketModule:
    return MarketModule(
        MockMarketDataProvider(), InMemoryMarketRepository(), MarketCache(), AsyncEventBus()
    )


class TestMetadata:
    def test_name_and_capability(self) -> None:
        module = _make_module()
        assert module.metadata.name == "market"
        assert Capability.MARKET_DATA in module.metadata.capabilities


class TestLifecycle:
    async def test_start_connects_provider(self) -> None:
        module = _make_module()
        await module.on_start()
        assert await module.service.provider.is_connected()

    async def test_stop_disconnects_provider(self) -> None:
        module = _make_module()
        await module.on_start()
        await module.on_stop()
        assert not await module.service.provider.is_connected()


class TestHealth:
    async def test_healthy_when_connected(self) -> None:
        module = _make_module()
        await module.on_start()
        result = await module.check_health()
        assert result.status == HealthStatus.HEALTHY

    async def test_unavailable_when_disconnected(self) -> None:
        module = _make_module()
        result = await module.check_health()
        assert result.status == HealthStatus.UNAVAILABLE
