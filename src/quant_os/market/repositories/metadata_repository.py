"""In-memory implementation of MetadataRepository."""

from __future__ import annotations

from quant_os.market.models.market_metadata import MarketMetadata
from quant_os.market.models.symbol import Symbol


class InMemoryMetadataRepository:
    """An in-memory :class:`~quant_os.market.interfaces.repositories.MetadataRepository`.

    Retains only the latest metadata snapshot per symbol. Not persisted
    across process restarts.
    """

    def __init__(self) -> None:
        """Initialize an empty repository."""
        self._metadata: dict[Symbol, MarketMetadata] = {}

    async def save(self, metadata: MarketMetadata) -> None:
        """Persist a metadata snapshot, replacing any previous one for its symbol.

        Args:
            metadata: The metadata to persist.
        """
        self._metadata[metadata.asset.symbol] = metadata

    async def get(self, symbol: Symbol) -> MarketMetadata | None:
        """Retrieve the most recently stored metadata for a symbol.

        Args:
            symbol: The instrument to look up.

        Returns:
            The latest stored metadata, or ``None`` if none exists.
        """
        return self._metadata.get(symbol)
