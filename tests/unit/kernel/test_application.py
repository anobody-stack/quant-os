"""Unit tests for the Application kernel orchestrator."""

from __future__ import annotations

import pytest

from quant_os.core.config import DevelopmentSettings
from quant_os.core.types import Version
from quant_os.kernel.application import Application
from quant_os.kernel.bootstrap import build_container
from quant_os.kernel.exceptions import ModuleDependencyError, ShutdownError, StartupError
from quant_os.kernel.health import HealthCheckResult, HealthStatus
from quant_os.kernel.lifecycle import ModuleState
from quant_os.kernel.module import Module, ModuleMetadata


def _make_app() -> Application:
    return Application(build_container(DevelopmentSettings()))


class RecordingModule(Module):
    def __init__(self, name: str, dependencies: tuple[str, ...] = ()) -> None:
        self._name = name
        self._dependencies = dependencies
        self.events: list[str] = []

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name=self._name,
            version=Version(1, 0, 0),
            description="test module",
            dependencies=self._dependencies,
        )

    async def on_initialize(self) -> None:
        self.events.append("initialize")

    async def on_start(self) -> None:
        self.events.append("start")

    async def on_stop(self) -> None:
        self.events.append("stop")

    async def on_dispose(self) -> None:
        self.events.append("dispose")

    async def check_health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY)


class FailingInitModule(Module):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(name="failing_init", version=Version(1, 0, 0), description="d")

    async def on_initialize(self) -> None:
        raise RuntimeError("init failed")


class FailingStartModule(Module):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(name="failing_start", version=Version(1, 0, 0), description="d")

    async def on_start(self) -> None:
        raise RuntimeError("start failed")


class FailingStopModule(Module):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(name="failing_stop", version=Version(1, 0, 0), description="d")

    async def on_stop(self) -> None:
        raise RuntimeError("stop failed")


class TestModuleRegistration:
    def test_register_module_tracks_it_in_lifecycle_manager(self) -> None:
        app = _make_app()
        app.register_module(RecordingModule("a"))
        assert app.lifecycle.get_state("a") == ModuleState.CREATED

    def test_duplicate_registration_raises(self) -> None:
        app = _make_app()
        app.register_module(RecordingModule("a"))
        with pytest.raises(ModuleDependencyError):
            app.register_module(RecordingModule("a"))

    def test_registering_with_unregistered_dependency_raises(self) -> None:
        app = _make_app()
        with pytest.raises(ModuleDependencyError):
            app.register_module(RecordingModule("b", dependencies=("a",)))

    def test_registering_with_satisfied_dependency_succeeds(self) -> None:
        app = _make_app()
        app.register_module(RecordingModule("a"))
        app.register_module(RecordingModule("b", dependencies=("a",)))
        assert app.get_module("b").metadata.name == "b"

    def test_get_module_unknown_raises(self) -> None:
        app = _make_app()
        with pytest.raises(ModuleDependencyError):
            app.get_module("unknown")


class TestInitializeAndStart:
    async def test_initialize_runs_hook(self) -> None:
        app = _make_app()
        module = RecordingModule("a")
        app.register_module(module)
        await app.initialize()
        assert module.events == ["initialize"]
        assert app.lifecycle.get_state("a") == ModuleState.INITIALIZED

    async def test_start_runs_after_initialize(self) -> None:
        app = _make_app()
        module = RecordingModule("a")
        app.register_module(module)
        await app.initialize()
        await app.start()
        assert module.events == ["initialize", "start"]
        assert app.lifecycle.get_state("a") == ModuleState.READY

    async def test_modules_initialized_in_dependency_order(self) -> None:
        app = _make_app()
        order: list[str] = []

        class OrderTrackingModule(Module):
            def __init__(self, name: str, dependencies: tuple[str, ...] = ()) -> None:
                self._name = name
                self._dependencies = dependencies

            @property
            def metadata(self) -> ModuleMetadata:
                return ModuleMetadata(
                    name=self._name,
                    version=Version(1, 0, 0),
                    description="d",
                    dependencies=self._dependencies,
                )

            async def on_initialize(self) -> None:
                order.append(self._name)

        app.register_module(OrderTrackingModule("base"))
        app.register_module(OrderTrackingModule("dependent", dependencies=("base",)))
        await app.initialize()
        assert order == ["base", "dependent"]

    async def test_initialize_failure_raises_startup_error(self) -> None:
        app = _make_app()
        app.register_module(FailingInitModule())
        with pytest.raises(StartupError):
            await app.initialize()
        assert app.lifecycle.get_state("failing_init") == ModuleState.FAILED

    async def test_start_failure_raises_startup_error(self) -> None:
        app = _make_app()
        app.register_module(FailingStartModule())
        await app.initialize()
        with pytest.raises(StartupError):
            await app.start()
        assert app.lifecycle.get_state("failing_start") == ModuleState.FAILED


class TestHealthChecks:
    async def test_run_health_checks_aggregates_module_results(self) -> None:
        app = _make_app()
        app.register_module(RecordingModule("a"))
        report = await app.run_health_checks()
        assert report.results["a"].status == HealthStatus.HEALTHY
        assert report.overall_status == HealthStatus.HEALTHY


class TestShutdown:
    async def test_shutdown_runs_stop_and_dispose(self) -> None:
        app = _make_app()
        module = RecordingModule("a")
        app.register_module(module)
        await app.initialize()
        await app.start()
        await app.shutdown()
        assert module.events == ["initialize", "start", "stop", "dispose"]
        assert app.lifecycle.get_state("a") == ModuleState.DISPOSED

    async def test_shutdown_runs_in_reverse_dependency_order(self) -> None:
        app = _make_app()
        order: list[str] = []

        class OrderTrackingModule(Module):
            def __init__(self, name: str, dependencies: tuple[str, ...] = ()) -> None:
                self._name = name
                self._dependencies = dependencies

            @property
            def metadata(self) -> ModuleMetadata:
                return ModuleMetadata(
                    name=self._name,
                    version=Version(1, 0, 0),
                    description="d",
                    dependencies=self._dependencies,
                )

            async def on_stop(self) -> None:
                order.append(self._name)

        app.register_module(OrderTrackingModule("base"))
        app.register_module(OrderTrackingModule("dependent", dependencies=("base",)))
        await app.initialize()
        await app.start()
        await app.shutdown()
        assert order == ["dependent", "base"]

    async def test_shutdown_continues_after_one_module_fails(self) -> None:
        app = _make_app()
        healthy_module = RecordingModule("healthy")
        app.register_module(FailingStopModule())
        app.register_module(healthy_module)
        await app.initialize()
        await app.start()
        with pytest.raises(ShutdownError):
            await app.shutdown()
        # The healthy module should still have been shut down despite the other's failure.
        assert healthy_module.events == ["initialize", "start", "stop", "dispose"]

    async def test_shutdown_skips_modules_never_started(self) -> None:
        app = _make_app()
        module = RecordingModule("a")
        app.register_module(module)
        await app.shutdown()  # never initialized/started
        assert module.events == []
