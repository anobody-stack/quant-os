"""Unit tests for the plugin foundation (interfaces only)."""

from __future__ import annotations

import pytest

from quant_os.core.types import Version
from quant_os.kernel.plugin import Plugin, PluginManager, PluginMetadata


class _ConcretePlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="sample",
            version=Version(1, 0, 0),
            description="a sample plugin",
            entry_point="quant_os.example:SamplePlugin",
        )


class _ConformingManager:
    async def load(self, metadata: PluginMetadata) -> Plugin:
        return _ConcretePlugin()

    async def unload(self, plugin_name: str) -> None:
        return None

    def list_loaded(self) -> list[PluginMetadata]:
        return []


class _NonConformingManager:
    pass


def test_plugin_metadata_fields() -> None:
    plugin = _ConcretePlugin()
    assert plugin.metadata.name == "sample"
    assert plugin.metadata.entry_point == "quant_os.example:SamplePlugin"


def test_plugin_is_abstract() -> None:
    with pytest.raises(TypeError):
        Plugin()  # type: ignore[abstract]


def test_conforming_manager_satisfies_protocol() -> None:
    assert isinstance(_ConformingManager(), PluginManager)


def test_non_conforming_manager_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingManager(), PluginManager)


async def test_conforming_manager_methods_are_callable() -> None:
    manager = _ConformingManager()
    metadata = PluginMetadata(
        name="sample", version=Version(1, 0, 0), description="d", entry_point="a:b"
    )
    plugin = await manager.load(metadata)
    assert isinstance(plugin, Plugin)
    await manager.unload("sample")
    assert manager.list_loaded() == []
