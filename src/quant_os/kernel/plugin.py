"""Plugin foundation: interfaces only.

Plugin *loading* (discovery, import, sandboxing, etc.) is explicitly out
of scope for this milestone. This module defines the shape future plugin
infrastructure will conform to.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from quant_os.core.types import Version


class PluginMetadata(BaseModel):
    """Static, self-describing information about a plugin.

    Attributes:
        name: A unique, stable identifier for the plugin.
        version: The plugin's own version.
        description: A short human-readable description of the plugin.
        entry_point: A dotted-path reference to the plugin's importable
            entry point. Not resolved or imported by anything in this
            milestone.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    version: Version
    description: str
    entry_point: str


class Plugin(ABC):
    """Base class future third-party or first-party plugins will implement.

    No plugin loading mechanism exists yet; this class only defines the
    shape a plugin must have once loading infrastructure is built.
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """This plugin's static metadata.

        Returns:
            The plugin's :class:`PluginMetadata`.
        """
        raise NotImplementedError


@runtime_checkable
class PluginManager(Protocol):
    """Abstraction for discovering, loading, and unloading plugins.

    This is an interface only — no concrete loading, discovery, or
    sandboxing mechanism is implemented here.
    """

    async def load(self, metadata: PluginMetadata) -> Plugin:
        """Load a plugin described by ``metadata``.

        Args:
            metadata: Metadata identifying the plugin to load.

        Returns:
            The loaded :class:`Plugin` instance.
        """
        ...

    async def unload(self, plugin_name: str) -> None:
        """Unload a previously loaded plugin.

        Args:
            plugin_name: The name of the plugin to unload.
        """
        ...

    def list_loaded(self) -> list[PluginMetadata]:
        """List metadata for all currently loaded plugins.

        Returns:
            Metadata for every currently loaded plugin.
        """
        ...
