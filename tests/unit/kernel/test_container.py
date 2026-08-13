"""Unit tests for the dependency injection container."""

from __future__ import annotations

import pytest

from quant_os.kernel.container import Container
from quant_os.kernel.exceptions import (
    CircularDependencyError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
    ServiceNotRegisteredError,
)
from quant_os.kernel.service import ServiceLifetime


class Greeter:
    def greet(self) -> str:
        return "hello"


class GreeterConsumer:
    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


class NoDependencies:
    pass


class WithDefaultParam:
    def __init__(self, value: int = 42) -> None:
        self.value = value


class Cyclic1:
    def __init__(self, other: Cyclic2) -> None:
        self.other = other


class Cyclic2:
    def __init__(self, other: Cyclic1) -> None:
        self.other = other


class UntypedParam:
    def __init__(self, mystery) -> None:  # type: ignore[no-untyped-def]
        self.mystery = mystery


class TestSingletonLifetime:
    def test_returns_same_instance_across_resolutions(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        first = container.resolve(Greeter)
        second = container.resolve(Greeter)
        assert first is second

    def test_instance_registration(self) -> None:
        container = Container()
        instance = Greeter()
        container.register_singleton(Greeter, instance=instance)
        assert container.resolve(Greeter) is instance

    def test_factory_registration(self) -> None:
        container = Container()
        container.register_singleton(Greeter, factory=lambda c: Greeter())
        first = container.resolve(Greeter)
        second = container.resolve(Greeter)
        assert first is second


class TestTransientLifetime:
    def test_returns_new_instance_each_time(self) -> None:
        container = Container()
        container.register_transient(Greeter, Greeter)
        first = container.resolve(Greeter)
        second = container.resolve(Greeter)
        assert first is not second


class TestScopedLifetime:
    def test_same_instance_within_scope(self) -> None:
        container = Container()
        container.register_scoped(Greeter, Greeter)
        with container.create_scope() as scope:
            first = container.resolve(Greeter, scope=scope)
            second = container.resolve(Greeter, scope=scope)
        assert first is second

    def test_different_instance_across_scopes(self) -> None:
        container = Container()
        container.register_scoped(Greeter, Greeter)
        with container.create_scope() as scope_a:
            a = container.resolve(Greeter, scope=scope_a)
        with container.create_scope() as scope_b:
            b = container.resolve(Greeter, scope=scope_b)
        assert a is not b

    def test_resolving_scoped_without_scope_raises(self) -> None:
        container = Container()
        container.register_scoped(Greeter, Greeter)
        with pytest.raises(InvalidRegistrationError):
            container.resolve(Greeter)

    def test_scope_clears_on_exit(self) -> None:
        container = Container()
        container.register_scoped(Greeter, Greeter)
        scope = container.create_scope()
        with scope:
            container.resolve(Greeter, scope=scope)
        assert scope.instances == {}


class TestConstructorInjection:
    def test_resolves_nested_dependency(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        container.register_transient(GreeterConsumer, GreeterConsumer)
        consumer = container.resolve(GreeterConsumer)
        assert consumer.greeter.greet() == "hello"

    def test_no_dependency_constructor(self) -> None:
        container = Container()
        container.register_transient(NoDependencies, NoDependencies)
        assert isinstance(container.resolve(NoDependencies), NoDependencies)

    def test_uses_default_when_dependency_unregistered(self) -> None:
        container = Container()
        container.register_transient(WithDefaultParam, WithDefaultParam)
        result = container.resolve(WithDefaultParam)
        assert result.value == 42

    def test_untyped_required_param_raises(self) -> None:
        container = Container()
        container.register_transient(UntypedParam, UntypedParam)
        with pytest.raises(InvalidRegistrationError):
            container.resolve(UntypedParam)


class TestCircularDependencyDetection:
    def test_direct_cycle_raises(self) -> None:
        container = Container()
        container.register_transient(Cyclic1, Cyclic1)
        container.register_transient(Cyclic2, Cyclic2)
        with pytest.raises(CircularDependencyError):
            container.resolve(Cyclic1)


class TestServiceNotRegistered:
    def test_resolving_unregistered_type_raises(self) -> None:
        container = Container()
        with pytest.raises(ServiceNotRegisteredError):
            container.resolve(Greeter)

    def test_dependency_of_unregistered_type_raises(self) -> None:
        container = Container()
        container.register_transient(GreeterConsumer, GreeterConsumer)
        with pytest.raises(ServiceNotRegisteredError):
            container.resolve(GreeterConsumer)


class TestRegistrationValidation:
    def test_registering_without_implementation_factory_or_instance_raises(self) -> None:
        container = Container()
        with pytest.raises(InvalidRegistrationError):
            container.register_singleton(Greeter)

    def test_duplicate_registration_raises(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        with pytest.raises(DuplicateRegistrationError):
            container.register_singleton(Greeter, Greeter)

    def test_override_allows_duplicate(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        container.register_singleton(Greeter, Greeter, override=True)
        assert container.is_registered(Greeter)


class TestServiceReplacement:
    def test_replace_swaps_implementation(self) -> None:
        container = Container()

        class FakeGreeter(Greeter):
            def greet(self) -> str:
                return "fake"

        container.register_singleton(Greeter, Greeter)
        container.resolve(Greeter)  # cache the original singleton
        container.replace(Greeter, FakeGreeter)
        assert container.resolve(Greeter).greet() == "fake"

    def test_replace_with_instance(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        replacement = Greeter()
        container.replace(Greeter, instance=replacement)
        assert container.resolve(Greeter) is replacement


class TestUnregisterAndIsRegistered:
    def test_is_registered_true_after_registration(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        assert container.is_registered(Greeter)

    def test_is_registered_false_before_registration(self) -> None:
        container = Container()
        assert not container.is_registered(Greeter)

    def test_unregister_removes_registration(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        container.unregister(Greeter)
        assert not container.is_registered(Greeter)

    def test_unregister_unknown_type_is_a_no_op(self) -> None:
        container = Container()
        container.unregister(Greeter)  # must not raise


class TestRegisterFactory:
    def test_register_factory_defaults_to_transient(self) -> None:
        container = Container()
        container.register_factory(Greeter, lambda c: Greeter())
        first = container.resolve(Greeter)
        second = container.resolve(Greeter)
        assert first is not second

    def test_register_factory_with_explicit_lifetime(self) -> None:
        container = Container()
        container.register_factory(Greeter, lambda c: Greeter(), lifetime=ServiceLifetime.SINGLETON)
        first = container.resolve(Greeter)
        second = container.resolve(Greeter)
        assert first is second


class TestValidateGraph:
    def test_valid_graph_does_not_raise(self) -> None:
        container = Container()
        container.register_singleton(Greeter, Greeter)
        container.register_transient(GreeterConsumer, GreeterConsumer)
        container.validate_graph()  # must not raise

    def test_missing_dependency_raises(self) -> None:
        container = Container()
        container.register_transient(GreeterConsumer, GreeterConsumer)
        with pytest.raises(ServiceNotRegisteredError):
            container.validate_graph()

    def test_circular_dependency_raises(self) -> None:
        container = Container()
        container.register_transient(Cyclic1, Cyclic1)
        container.register_transient(Cyclic2, Cyclic2)
        with pytest.raises(CircularDependencyError):
            container.validate_graph()

    def test_factory_registration_skips_signature_check(self) -> None:
        container = Container()
        container.register_singleton(Greeter, factory=lambda c: Greeter())
        container.validate_graph()  # must not raise

    def test_untyped_required_param_raises_during_validation(self) -> None:
        container = Container()
        container.register_transient(UntypedParam, UntypedParam)
        with pytest.raises(InvalidRegistrationError):
            container.validate_graph()
