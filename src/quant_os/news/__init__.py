"""News domain: providers and repositories for financial news.

This package currently exposes interfaces only
(:class:`~quant_os.news.provider.NewsProvider`,
:class:`~quant_os.news.repository.NewsRepository`). Concrete
implementations, classification, and scoring are reserved for later
milestones.
"""

from quant_os.news.provider import NewsProvider
from quant_os.news.repository import NewsRepository

__all__ = ["NewsProvider", "NewsRepository"]
