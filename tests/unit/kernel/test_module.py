"""Unit tests for the Module abstraction."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from quant_os.core.types import Version
from quant_os.kernel.capabilities import Capability
from quant_os.kernel.health import HealthStatus
from quant_os.kernel.module import Module, ModuleMetadata


class MinimalModule(Module):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(name="minimal", version=Version(1, 0, 0), description="test")


class FullModule(Module):
    def __init__(self) -> None:
        self.events: list[str] = []

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="full",
            version=Version(2, 1, 0),
            description="a fully-hooked module",
            dependencies=("minimal",),
            capabilities=(Capability.NEWS, Capability.MACRO),
        )

    async def on_initialize(self) -> None:
        self.events.append("initialize")

    async def on_start(self) -> None:
        self.events.append("start")

    async def on_stop(self) -> None:
        self.events.append("stop")

    async def on_dispose(self) -> None:
        self.events.append("dispose")


class TestModuleMetadata:
    def test_defaults(self) -> None:
        metadata = ModuleMetadata(name="x", version=Version(1, 0, 0), description="d")
        assert metadata.dependencies == ()
        assert metadata.capabilities == ()

    def test_explicit_dependencies_and_capabilities(self) -> None:
        metadata = ModuleMetadata(
            name="x",
            version=Version(1, 0, 0),
            description="d",
            dependencies=("a", "b"),
            capabilities=(Capability.RISK,),
        )
        assert metadata.dependencies == ("a", "b")
        assert metadata.capabilities == (Capability.RISK,)

    def test_is_immutable(self) -> None:
        metadata = ModuleMetadata(name="x", version=Version(1, 0, 0), description="d")
        with pytest.raises(PydanticValidationError):
            metadata.name = "y"  # type: ignore[misc]


class TestModuleDefaults:
    async def test_default_lifecycle_hooks_are_no_ops(self) -> None:
        module = MinimalModule()
        await module.on_initialize()
        await module.on_start()
        await module.on_stop()
        await module.on_dispose()  # must not raise

    async def test_default_health_is_unknown(self) -> None:
        module = MinimalModule()
        result = await module.check_health()
        assert result.status == HealthStatus.UNKNOWN

    def test_metadata_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            Module()  # type: ignore[abstract]


class TestModuleOverrides:
    async def test_hooks_run_in_order(self) -> None:
        module = FullModule()
        await module.on_initialize()
        await module.on_start()
        await module.on_stop()
        await module.on_dispose()
        assert module.events == ["initialize", "start", "stop", "dispose"]

    def test_metadata_reflects_dependencies_and_capabilities(self) -> None:
        module = FullModule()
        assert module.metadata.dependencies == ("minimal",)
        assert Capability.NEWS in module.metadata.capabilities
