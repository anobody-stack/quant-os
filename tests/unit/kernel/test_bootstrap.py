"""Unit tests for kernel bootstrap."""

from __future__ import annotations

from quant_os.core.config import DevelopmentSettings, Settings
from quant_os.events import AsyncEventBus, EventBus
from quant_os.kernel.bootstrap import build_container
from quant_os.kernel.health import HealthAggregator
from quant_os.kernel.lifecycle import LifecycleManager


def test_registers_settings() -> None:
    settings = DevelopmentSettings()
    container = build_container(settings)
    assert container.resolve(Settings) is settings


def test_registers_event_bus_as_async_event_bus() -> None:
    container = build_container(DevelopmentSettings())
    bus = container.resolve(EventBus)
    assert isinstance(bus, AsyncEventBus)


def test_event_bus_is_singleton() -> None:
    container = build_container(DevelopmentSettings())
    first = container.resolve(EventBus)
    second = container.resolve(EventBus)
    assert first is second


def test_registers_lifecycle_manager() -> None:
    container = build_container(DevelopmentSettings())
    assert isinstance(container.resolve(LifecycleManager), LifecycleManager)


def test_registers_health_aggregator() -> None:
    container = build_container(DevelopmentSettings())
    assert isinstance(container.resolve(HealthAggregator), HealthAggregator)


def test_defaults_to_process_settings_when_none_given() -> None:
    container = build_container()
    assert isinstance(container.resolve(Settings), Settings)
