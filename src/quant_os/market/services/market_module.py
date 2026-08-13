"""MarketModule: plugs the Market Data Engine into the Application Kernel."""

from __future__ import annotations

from quant_os.core.types import Version
from quant_os.events import EventBus
from quant_os.kernel.capabilities import Capability
from quant_os.kernel.health import HealthCheckResult, HealthStatus
from quant_os.kernel.module import Module, ModuleMetadata
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.interfaces.providers import MarketDataProvider
from quant_os.market.interfaces.repositories import MarketRepository
from quant_os.market.services.market_service import MarketService
from quant_os.market.subscriptions.subscription_manager import SubscriptionManager


class MarketModule(Module):
    """The Kernel module wrapping the Market Data Engine.

    Registers the :attr:`~quant_os.kernel.capabilities.Capability.MARKET_DATA`
    capability, connects the configured provider on start, disconnects it
    on stop, and reports health based on the provider's connection state.
    """

    def __init__(
        self,
        provider: MarketDataProvider,
        repository: MarketRepository,
        cache: MarketCache,
        event_bus: EventBus,
    ) -> None:
        """Initialize the market module and its dependencies.

        All dependencies are expected to arrive via constructor injection
        from the Kernel's DI container — this module never loads
        configuration or constructs its own dependencies.

        Args:
            provider: The market data provider to use.
            repository: The repository to persist data to.
            cache: The cache to serve fast reads from.
            event_bus: The event bus to publish market events on.
        """
        self.service = MarketService(provider, repository, cache, event_bus)
        self.subscriptions = SubscriptionManager(event_bus)

    @property
    def metadata(self) -> ModuleMetadata:
        """This module's static metadata.

        Returns:
            The module's :class:`~quant_os.kernel.module.ModuleMetadata`.
        """
        return ModuleMetadata(
            name="market",
            version=Version(1, 0, 0),
            description="Market Data Engine: the single source of truth for market prices.",
            capabilities=(Capability.MARKET_DATA,),
        )

    async def on_start(self) -> None:
        """Connect the provider and start dispatching subscriptions."""
        await self.service.connect()
        await self.subscriptions.start()

    async def on_stop(self) -> None:
        """Stop dispatching subscriptions and disconnect the provider."""
        await self.subscriptions.stop()
        await self.service.disconnect(reason="module stopped")

    async def check_health(self) -> HealthCheckResult:
        """Report health based on the underlying provider's connection state.

        Returns:
            :data:`~quant_os.kernel.health.HealthStatus.HEALTHY` if the
            provider is connected,
            :data:`~quant_os.kernel.health.HealthStatus.UNAVAILABLE`
            otherwise.
        """
        connected = await self.service.provider.is_connected()
        if connected:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Provider connected",
                details={"subscriptions": str(self.subscriptions.listener_count)},
            )
        return HealthCheckResult(status=HealthStatus.UNAVAILABLE, message="Provider disconnected")
