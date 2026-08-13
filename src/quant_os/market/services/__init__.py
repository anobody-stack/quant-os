"""The Market Service: the central entry point for market data, plus its
Kernel module wrapper.
"""

from quant_os.market.services.market_module import MarketModule
from quant_os.market.services.market_service import MarketService

__all__ = ["MarketModule", "MarketService"]
