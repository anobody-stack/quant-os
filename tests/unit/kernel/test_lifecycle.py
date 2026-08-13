"""Unit tests for the lifecycle manager."""

from __future__ import annotations

import pytest

from quant_os.kernel.exceptions import ModuleLifecycleError
from quant_os.kernel.lifecycle import LifecycleManager, ModuleState


class TestRegisterAndGetState:
    def test_new_module_starts_created(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        assert manager.get_state("mod") == ModuleState.CREATED

    def test_get_state_unknown_module_raises(self) -> None:
        manager = LifecycleManager()
        with pytest.raises(ModuleLifecycleError):
            manager.get_state("unknown")


class TestValidTransitions:
    def test_full_happy_path(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        manager.transition("mod", ModuleState.INITIALIZING)
        manager.transition("mod", ModuleState.INITIALIZED)
        manager.transition("mod", ModuleState.STARTING)
        manager.transition("mod", ModuleState.READY)
        manager.transition("mod", ModuleState.STOPPING)
        manager.transition("mod", ModuleState.STOPPED)
        manager.transition("mod", ModuleState.SHUTTING_DOWN)
        manager.transition("mod", ModuleState.DISPOSED)
        assert manager.get_state("mod") == ModuleState.DISPOSED

    def test_restart_from_stopped(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        manager.transition("mod", ModuleState.INITIALIZING)
        manager.transition("mod", ModuleState.INITIALIZED)
        manager.transition("mod", ModuleState.STARTING)
        manager.transition("mod", ModuleState.READY)
        manager.transition("mod", ModuleState.STOPPING)
        manager.transition("mod", ModuleState.STOPPED)
        manager.transition("mod", ModuleState.STARTING)
        assert manager.get_state("mod") == ModuleState.STARTING

    def test_restart_from_failed(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        manager.transition("mod", ModuleState.INITIALIZING)
        manager.transition("mod", ModuleState.FAILED)
        manager.transition("mod", ModuleState.INITIALIZING)
        assert manager.get_state("mod") == ModuleState.INITIALIZING

    def test_failure_from_ready(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        manager.transition("mod", ModuleState.INITIALIZING)
        manager.transition("mod", ModuleState.INITIALIZED)
        manager.transition("mod", ModuleState.STARTING)
        manager.transition("mod", ModuleState.READY)
        manager.transition("mod", ModuleState.FAILED)
        assert manager.get_state("mod") == ModuleState.FAILED

    def test_failed_to_shutting_down(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        manager.transition("mod", ModuleState.INITIALIZING)
        manager.transition("mod", ModuleState.FAILED)
        manager.transition("mod", ModuleState.SHUTTING_DOWN)
        assert manager.get_state("mod") == ModuleState.SHUTTING_DOWN


class TestInvalidTransitions:
    def test_cannot_skip_states(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        with pytest.raises(ModuleLifecycleError):
            manager.transition("mod", ModuleState.READY)

    def test_cannot_transition_from_disposed(self) -> None:
        manager = LifecycleManager()
        manager.register("mod")
        manager.transition("mod", ModuleState.INITIALIZING)
        manager.transition("mod", ModuleState.INITIALIZED)
        manager.transition("mod", ModuleState.STARTING)
        manager.transition("mod", ModuleState.READY)
        manager.transition("mod", ModuleState.STOPPING)
        manager.transition("mod", ModuleState.STOPPED)
        manager.transition("mod", ModuleState.SHUTTING_DOWN)
        manager.transition("mod", ModuleState.DISPOSED)
        with pytest.raises(ModuleLifecycleError):
            manager.transition("mod", ModuleState.INITIALIZING)

    def test_transition_unknown_module_raises(self) -> None:
        manager = LifecycleManager()
        with pytest.raises(ModuleLifecycleError):
            manager.transition("unknown", ModuleState.INITIALIZING)
