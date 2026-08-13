"""Structural conformance tests for the news interfaces."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

from quant_os.events.domain_events import NewsReceived
from quant_os.events.metadata import EventMetadata
from quant_os.news.provider import NewsProvider
from quant_os.news.repository import NewsRepository


def _make_article(title: str = "headline") -> NewsReceived:
    return NewsReceived(
        metadata=EventMetadata(source="test"),
        title=title,
        source_name="Test Source",
        published_at=datetime.now(UTC),
    )


class _ConformingProvider:
    async def get_latest_headlines(self, limit: int = 50) -> list[NewsReceived]:
        return [_make_article()]

    async def stream(self) -> AsyncIterator[NewsReceived]:
        yield _make_article()


class _NonConformingProvider:
    pass


class _ConformingRepository:
    async def save(self, article: NewsReceived) -> None:
        return None

    async def get_by_id(self, article_id: UUID) -> NewsReceived | None:
        return None

    async def list_recent(self, limit: int = 50) -> list[NewsReceived]:
        return []

    async def delete(self, article_id: UUID) -> None:
        return None


class _NonConformingRepository:
    pass


def test_conforming_provider_satisfies_protocol() -> None:
    assert isinstance(_ConformingProvider(), NewsProvider)


def test_non_conforming_provider_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingProvider(), NewsProvider)


def test_conforming_repository_satisfies_protocol() -> None:
    assert isinstance(_ConformingRepository(), NewsRepository)


def test_non_conforming_repository_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingRepository(), NewsRepository)
