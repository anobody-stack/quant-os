"""The dependency injection container.

Implements reflection-based constructor injection: a registered
implementation's ``__init__`` type hints are inspected to determine its
dependencies, which are resolved recursively from the same container.
"""

from __future__ import annotations

import inspect
import typing
from collections.abc import Callable
from typing import Any, TypeVar

from quant_os.core.logging import get_logger
from quant_os.kernel.exceptions import (
    CircularDependencyError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
    ServiceNotRegisteredError,
)
from quant_os.kernel.service import ServiceDescriptor, ServiceLifetime

_logger = get_logger(__name__)

T = TypeVar("T")


class Scope:
    """A resolution scope holding one cached instance per scoped service.

    Use via :meth:`Container.create_scope` as a context manager:

    .. code-block:: python

        with container.create_scope() as scope:
            service = container.resolve(MyService, scope=scope)
    """

    def __init__(self) -> None:
        """Initialize an empty scope."""
        self.instances: dict[type, object] = {}

    def __enter__(self) -> Scope:
        """Enter the scope's context, returning the scope itself."""
        return self

    def __exit__(self, *_exc_info: object) -> None:
        """Exit the scope's context, discarding all cached scoped instances."""
        self.instances.clear()


class Container:
    """A dependency injection container supporting singleton, transient,
    and scoped lifetimes, factory registration, and constructor injection.
    """

    def __init__(self) -> None:
        """Initialize an empty container with no registrations."""
        self._descriptors: dict[type, ServiceDescriptor] = {}
        self._singleton_instances: dict[type, object] = {}

    def register_singleton(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        instance: T | None = None,
        override: bool = False,
    ) -> None:
        """Register a service with singleton lifetime.

        Args:
            service_type: The type other code will resolve by.
            implementation: A concrete class to construct via constructor
                injection. Mutually exclusive with ``factory``/``instance``.
            factory: A callable taking the container and returning an
                instance. Mutually exclusive with ``implementation``/``instance``.
            instance: A pre-built instance to use directly. Mutually
                exclusive with ``implementation``/``factory``.
            override: If True, replaces any existing registration for
                ``service_type`` instead of raising.

        Raises:
            InvalidRegistrationError: If zero or more than one of
                ``implementation``, ``factory``, ``instance`` is given.
            DuplicateRegistrationError: If ``service_type`` is already
                registered and ``override`` is False.
        """
        self._register(
            service_type,
            ServiceLifetime.SINGLETON,
            implementation=implementation,
            factory=factory,
            instance=instance,
            override=override,
        )
        if instance is not None:
            self._singleton_instances[service_type] = instance

    def register_transient(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        override: bool = False,
    ) -> None:
        """Register a service with transient lifetime (a new instance per resolution).

        Args:
            service_type: The type other code will resolve by.
            implementation: A concrete class to construct via constructor
                injection. Mutually exclusive with ``factory``.
            factory: A callable taking the container and returning an
                instance. Mutually exclusive with ``implementation``.
            override: If True, replaces any existing registration for
                ``service_type`` instead of raising.

        Raises:
            InvalidRegistrationError: If zero or both of ``implementation``
                and ``factory`` are given.
            DuplicateRegistrationError: If ``service_type`` is already
                registered and ``override`` is False.
        """
        self._register(
            service_type,
            ServiceLifetime.TRANSIENT,
            implementation=implementation,
            factory=factory,
            override=override,
        )

    def register_scoped(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        override: bool = False,
    ) -> None:
        """Register a service with scoped lifetime (one instance per :class:`Scope`).

        Args:
            service_type: The type other code will resolve by.
            implementation: A concrete class to construct via constructor
                injection. Mutually exclusive with ``factory``.
            factory: A callable taking the container and returning an
                instance. Mutually exclusive with ``implementation``.
            override: If True, replaces any existing registration for
                ``service_type`` instead of raising.

        Raises:
            InvalidRegistrationError: If zero or both of ``implementation``
                and ``factory`` are given.
            DuplicateRegistrationError: If ``service_type`` is already
                registered and ``override`` is False.
        """
        self._register(
            service_type,
            ServiceLifetime.SCOPED,
            implementation=implementation,
            factory=factory,
            override=override,
        )

    def register_factory(
        self,
        service_type: type[T],
        factory: Callable[[Container], T],
        *,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        override: bool = False,
    ) -> None:
        """Register a service constructed by a factory callable.

        Convenience wrapper equivalent to calling the corresponding
        ``register_*`` method with ``factory=factory``.

        Args:
            service_type: The type other code will resolve by.
            factory: A callable taking the container and returning an
                instance.
            lifetime: The lifetime to register the factory under.
            override: If True, replaces any existing registration for
                ``service_type`` instead of raising.
        """
        self._register(service_type, lifetime, factory=factory, override=override)

    def replace(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        instance: T | None = None,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None:
        """Replace an existing (or add a new) registration for ``service_type``.

        Equivalent to calling the corresponding ``register_*`` method with
        ``override=True``. Primarily useful for tests that need to swap in
        a fake/mock implementation.

        Args:
            service_type: The type to replace the registration for.
            implementation: A concrete class to construct via constructor
                injection.
            factory: A callable taking the container and returning an
                instance.
            instance: A pre-built instance to use directly.
            lifetime: The lifetime to register the replacement under.
        """
        self._singleton_instances.pop(service_type, None)
        self._register(
            service_type,
            lifetime,
            implementation=implementation,
            factory=factory,
            instance=instance,
            override=True,
        )
        if instance is not None:
            self._singleton_instances[service_type] = instance

    def is_registered(self, service_type: type) -> bool:
        """Check whether a service type has a registration.

        Args:
            service_type: The type to check.

        Returns:
            True if ``service_type`` is registered, False otherwise.
        """
        return service_type in self._descriptors

    def unregister(self, service_type: type) -> None:
        """Remove a service registration, if present.

        Args:
            service_type: The type to remove. Removing an unregistered
                type is a no-op.
        """
        self._descriptors.pop(service_type, None)
        self._singleton_instances.pop(service_type, None)

    def create_scope(self) -> Scope:
        """Create a new resolution scope for scoped service lifetimes.

        Returns:
            A new, empty :class:`Scope`.
        """
        return Scope()

    def resolve(self, service_type: type[T], *, scope: Scope | None = None) -> T:
        """Resolve an instance of ``service_type``, constructing it if needed.

        Args:
            service_type: The type to resolve.
            scope: The scope to use for scoped-lifetime services. Required
                only if resolving (directly or transitively) a service
                registered with :attr:`ServiceLifetime.SCOPED`.

        Returns:
            An instance of ``service_type``.

        Raises:
            ServiceNotRegisteredError: If ``service_type`` (or a transitive
                dependency) has no registration.
            CircularDependencyError: If resolving ``service_type`` would
                require resolving itself, directly or transitively.
        """
        return self._resolve(service_type, scope=scope, stack=[])

    def validate_graph(self) -> None:
        """Validate that every registered service's dependencies are
        resolvable, without actually constructing any instances.

        Raises:
            ServiceNotRegisteredError: If any registered implementation
                depends on an unregistered type.
            CircularDependencyError: If the dependency graph contains a
                cycle.
        """
        for service_type in list(self._descriptors):
            self._validate(service_type, stack=[])

    def _register(
        self,
        service_type: type,
        lifetime: ServiceLifetime,
        *,
        implementation: type | None = None,
        factory: Callable[[Container], object] | None = None,
        instance: object | None = None,
        override: bool = False,
    ) -> None:
        provided = sum(x is not None for x in (implementation, factory, instance))
        if provided != 1:
            raise InvalidRegistrationError(
                "Exactly one of implementation, factory, or instance must be provided",
                context={"service_type": service_type.__name__, "provided_count": provided},
            )
        if not override and service_type in self._descriptors:
            raise DuplicateRegistrationError(
                f"{service_type.__name__} is already registered",
                context={"service_type": service_type.__name__},
            )
        self._descriptors[service_type] = ServiceDescriptor(
            service_type=service_type,
            lifetime=lifetime,
            implementation=implementation,
            factory=factory,
            instance=instance,
        )
        _logger.debug(
            "Registered service",
            extra={
                "service_type": service_type.__name__,
                "lifetime": lifetime.value,
                "override": override,
            },
        )

    def _resolve(self, service_type: type[T], *, scope: Scope | None, stack: list[type]) -> T:
        if service_type in stack:
            chain = " -> ".join(t.__name__ for t in (*stack, service_type))
            raise CircularDependencyError(
                f"Circular dependency detected: {chain}",
                context={"chain": [t.__name__ for t in (*stack, service_type)]},
            )

        descriptor = self._descriptors.get(service_type)
        if descriptor is None:
            raise ServiceNotRegisteredError(
                f"No registration found for {service_type.__name__}",
                context={"service_type": service_type.__name__},
            )

        if descriptor.lifetime is ServiceLifetime.SINGLETON:
            if service_type in self._singleton_instances:
                return typing.cast("T", self._singleton_instances[service_type])
            instance = self._construct(descriptor, scope=scope, stack=[*stack, service_type])
            self._singleton_instances[service_type] = instance
            return typing.cast("T", instance)

        if descriptor.lifetime is ServiceLifetime.SCOPED:
            if scope is None:
                raise InvalidRegistrationError(
                    f"{service_type.__name__} is scoped but no scope was provided",
                    context={"service_type": service_type.__name__},
                )
            if service_type in scope.instances:
                return typing.cast("T", scope.instances[service_type])
            instance = self._construct(descriptor, scope=scope, stack=[*stack, service_type])
            scope.instances[service_type] = instance
            return typing.cast("T", instance)

        # TRANSIENT
        return typing.cast(
            "T", self._construct(descriptor, scope=scope, stack=[*stack, service_type])
        )

    def _construct(
        self, descriptor: ServiceDescriptor, *, scope: Scope | None, stack: list[type]
    ) -> object:
        if descriptor.instance is not None:
            return descriptor.instance
        if descriptor.factory is not None:
            return descriptor.factory(self)
        if descriptor.implementation is None:
            raise InvalidRegistrationError(
                f"Service descriptor for {descriptor.service_type.__name__} has no "
                "implementation, factory, or instance",
                context={"service_type": descriptor.service_type.__name__},
            )
        kwargs = self._resolve_constructor_dependencies(
            descriptor.implementation, scope=scope, stack=stack
        )
        return descriptor.implementation(**kwargs)

    def _resolve_constructor_dependencies(
        self, implementation: type, *, scope: Scope | None, stack: list[type]
    ) -> dict[str, Any]:
        signature = inspect.signature(implementation.__init__)
        try:
            hints = typing.get_type_hints(implementation.__init__)
        except NameError:
            hints = {}

        kwargs: dict[str, Any] = {}
        for name, parameter in signature.parameters.items():
            if name == "self" or parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            dependency_type = hints.get(name)
            if dependency_type is None or not self.is_registered(dependency_type):
                if parameter.default is not inspect.Parameter.empty:
                    continue
                if dependency_type is None:
                    raise InvalidRegistrationError(
                        f"Cannot resolve parameter {name!r} of "
                        f"{implementation.__name__}: no type hint and no default",
                        context={"implementation": implementation.__name__, "parameter": name},
                    )
                raise ServiceNotRegisteredError(
                    f"No registration found for {dependency_type.__name__} "
                    f"(required by {implementation.__name__}.__init__ parameter {name!r})",
                    context={
                        "implementation": implementation.__name__,
                        "parameter": name,
                        "dependency_type": dependency_type.__name__,
                    },
                )
            kwargs[name] = self._resolve(dependency_type, scope=scope, stack=stack)
        return kwargs

    def _validate(self, service_type: type, *, stack: list[type]) -> None:
        if service_type in stack:
            chain = " -> ".join(t.__name__ for t in (*stack, service_type))
            raise CircularDependencyError(
                f"Circular dependency detected: {chain}",
                context={"chain": [t.__name__ for t in (*stack, service_type)]},
            )
        descriptor = self._descriptors.get(service_type)
        if descriptor is None:
            raise ServiceNotRegisteredError(
                f"No registration found for {service_type.__name__}",
                context={"service_type": service_type.__name__},
            )
        if descriptor.implementation is None:
            return
        signature = inspect.signature(descriptor.implementation.__init__)
        try:
            hints = typing.get_type_hints(descriptor.implementation.__init__)
        except NameError:
            hints = {}
        for name, parameter in signature.parameters.items():
            if name == "self" or parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            dependency_type = hints.get(name)
            if dependency_type is None or not self.is_registered(dependency_type):
                if parameter.default is not inspect.Parameter.empty:
                    continue
                if dependency_type is None:
                    raise InvalidRegistrationError(
                        f"Cannot resolve parameter {name!r} of "
                        f"{descriptor.implementation.__name__}: no type hint and no default",
                        context={
                            "implementation": descriptor.implementation.__name__,
                            "parameter": name,
                        },
                    )
                raise ServiceNotRegisteredError(
                    f"No registration found for {dependency_type.__name__} "
                    f"(required by {descriptor.implementation.__name__}.__init__ "
                    f"parameter {name!r})",
                    context={
                        "implementation": descriptor.implementation.__name__,
                        "parameter": name,
                        "dependency_type": dependency_type.__name__,
                    },
                )
            self._validate(dependency_type, stack=[*stack, service_type])
