"""End-to-end test: MarketModule registered with the real Kernel Application."""

from quant_os.core.config import DevelopmentSettings
from quant_os.events import EventBus
from quant_os.kernel.application import Application
from quant_os.kernel.bootstrap import build_container
from quant_os.kernel.health import HealthStatus
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.providers.mock_provider import MockMarketDataProvider
from quant_os.market.repositories.market_repository import InMemoryMarketRepository
from quant_os.market.services.market_module import MarketModule


async def test_market_module_full_lifecycle_through_application() -> None:
    container = build_container(DevelopmentSettings())
    event_bus = container.resolve(EventBus)
    module = MarketModule(
        MockMarketDataProvider(), InMemoryMarketRepository(), MarketCache(), event_bus
    )

    app = Application(container)
    app.register_module(module)

    await app.initialize()
    await app.start()

    report = await app.run_health_checks()
    assert report.results["market"].status == HealthStatus.HEALTHY

    await app.shutdown()
    assert not await module.service.provider.is_connected()
