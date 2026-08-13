"""Market data provider implementations.

Only a mock, synthetic provider exists at this milestone — no HTTP
requests, no real external services. Real providers (broker feeds,
vendor APIs) are reserved for a later milestone.
"""

from quant_os.market.providers.mock_provider import MockMarketDataProvider

__all__ = ["MockMarketDataProvider"]
