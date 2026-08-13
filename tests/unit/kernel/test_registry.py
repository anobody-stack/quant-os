"""Unit tests for the service registry."""

from __future__ import annotations

import pytest

from quant_os.kernel.container import Container
from quant_os.kernel.exceptions import ServiceNotRegisteredError
from quant_os.kernel.registry import ServiceRegistry
from quant_os.kernel.service import ServiceLifetime


class Widget:
    pass


class WidgetConsumer:
    def __init__(self, widget: Widget) -> None:
        self.widget = widget


class TestRegisterAndResolve:
    def test_register_singleton_and_resolve(self) -> None:
        registry = ServiceRegistry()
        registry.register_singleton(Widget, Widget)
        assert isinstance(registry.resolve(Widget), Widget)

    def test_register_transient_and_resolve(self) -> None:
        registry = ServiceRegistry()
        registry.register_transient(Widget, Widget)
        first = registry.resolve(Widget)
        second = registry.resolve(Widget)
        assert first is not second

    def test_register_scoped(self) -> None:
        registry = ServiceRegistry()
        registry.register_scoped(Widget, Widget)
        assert registry.exists(Widget)

    def test_constructor_injection_through_registry(self) -> None:
        registry = ServiceRegistry()
        registry.register_singleton(Widget, Widget)
        registry.register_transient(WidgetConsumer, WidgetConsumer)
        consumer = registry.resolve(WidgetConsumer)
        assert isinstance(consumer.widget, Widget)


class TestExistsAndRemove:
    def test_exists_true_after_registration(self) -> None:
        registry = ServiceRegistry()
        registry.register_singleton(Widget, Widget)
        assert registry.exists(Widget)

    def test_exists_false_before_registration(self) -> None:
        registry = ServiceRegistry()
        assert not registry.exists(Widget)

    def test_remove_clears_registration_and_metadata(self) -> None:
        registry = ServiceRegistry()
        registry.register_singleton(Widget, Widget)
        registry.remove(Widget)
        assert not registry.exists(Widget)
        with pytest.raises(ServiceNotRegisteredError):
            registry.get_metadata(Widget)


class TestOverride:
    def test_override_replaces_registration(self) -> None:
        registry = ServiceRegistry()
        registry.register_singleton(Widget, Widget)
        registry.resolve(Widget)
        replacement = Widget()
        registry.override(Widget, instance=replacement)
        assert registry.resolve(Widget) is replacement


class TestMetadata:
    def test_list_services_includes_registered_service(self) -> None:
        registry = ServiceRegistry()
        registry.register_singleton(Widget, Widget, description="a widget", registered_by="test")
        metadata_list = registry.list_services()
        names = [m.name for m in metadata_list]
        assert "Widget" in names

    def test_get_metadata_returns_correct_fields(self) -> None:
        registry = ServiceRegistry()
        registry.register_transient(Widget, Widget, description="a widget", registered_by="test")
        metadata = registry.get_metadata(Widget)
        assert metadata.lifetime == ServiceLifetime.TRANSIENT
        assert metadata.description == "a widget"
        assert metadata.registered_by == "test"

    def test_get_metadata_unregistered_raises(self) -> None:
        registry = ServiceRegistry()
        with pytest.raises(ServiceNotRegisteredError):
            registry.get_metadata(Widget)


def test_registry_can_wrap_existing_container() -> None:
    container = Container()
    registry = ServiceRegistry(container)
    registry.register_singleton(Widget, Widget)
    assert container.resolve(Widget) is registry.resolve(Widget)
