"""Market Data Engine.

The single source of truth for market prices inside QuantOS. No other
module accesses market data providers directly - every subsystem (AI,
strategies, risk, portfolio, execution, reporting) consumes market data
only through this package's :class:`~quant_os.market.services.MarketService`.

Subpackages:
    models: Strongly typed, immutable domain models.
    interfaces: Provider and repository contracts (no implementations).
    providers: Provider implementations (mock only, at this milestone).
    repositories: In-memory repository implementations.
    cache: TTL-based market data cache.
    validation: Validation beyond model-level constraints.
    subscriptions: Asset/timeframe-filtered subscriptions over the EventBus.
    events: Market-specific domain events, published on the EventBus.
    services: MarketService (entry point) and MarketModule (Kernel integration).
"""

from quant_os.market.assets import SUPPORTED_ASSETS, get_supported_asset
from quant_os.market.cache.market_cache import MarketCache
from quant_os.market.interfaces.providers import (
    HistoricalDataProvider,
    MarketDataProvider,
    MetadataProvider,
    QuoteProvider,
    StreamingProvider,
)
from quant_os.market.interfaces.repositories import (
    CandleRepository,
    MarketRepository,
    MetadataRepository,
    QuoteRepository,
    TickRepository,
)
from quant_os.market.services.market_module import MarketModule
from quant_os.market.services.market_service import MarketService
from quant_os.market.subscriptions.subscription_manager import (
    MarketSubscriptionId,
    SubscriptionFilter,
    SubscriptionManager,
)

__all__ = [
    "SUPPORTED_ASSETS",
    "CandleRepository",
    "HistoricalDataProvider",
    "MarketCache",
    "MarketDataProvider",
    "MarketModule",
    "MarketRepository",
    "MarketService",
    "MarketSubscriptionId",
    "MetadataProvider",
    "MetadataRepository",
    "QuoteProvider",
    "QuoteRepository",
    "StreamingProvider",
    "SubscriptionFilter",
    "SubscriptionManager",
    "TickRepository",
    "get_supported_asset",
]
