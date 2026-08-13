"""The service registry: a metadata-tracking catalog over the DI container."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

from quant_os.core.time import utc_now
from quant_os.kernel.container import Container
from quant_os.kernel.exceptions import ServiceNotRegisteredError
from quant_os.kernel.service import ServiceLifetime

T = TypeVar("T")


class ServiceMetadata(BaseModel):
    """Descriptive metadata about a registered service.

    Attributes:
        name: The registered type's qualified name.
        lifetime: The service's registered lifetime.
        description: An optional human-readable description.
        registered_by: The name of the module or component that
            registered this service, if known.
        registered_at: UTC time the service was registered.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    lifetime: ServiceLifetime
    description: str = ""
    registered_by: str | None = None
    registered_at: datetime = Field(default_factory=utc_now)


class ServiceRegistry:
    """A central catalog of registered services, layered over a :class:`Container`.

    The registry delegates actual construction and resolution to its
    underlying container, while additionally tracking descriptive
    :class:`ServiceMetadata` for introspection (listing, existence checks).
    """

    def __init__(self, container: Container | None = None) -> None:
        """Initialize a registry, optionally wrapping an existing container.

        Args:
            container: The container to delegate to. A new, empty
                :class:`Container` is created if not provided.
        """
        self.container = container if container is not None else Container()
        self._metadata: dict[type, ServiceMetadata] = {}

    def register_singleton(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        instance: T | None = None,
        description: str = "",
        registered_by: str | None = None,
        override: bool = False,
    ) -> None:
        """Register a singleton-lifetime service and record its metadata.

        Args:
            service_type: The type other code will resolve by.
            implementation: A concrete class to construct via constructor
                injection.
            factory: A callable taking the container and returning an
                instance.
            instance: A pre-built instance to use directly.
            description: A human-readable description of the service.
            registered_by: The name of the module or component
                registering this service.
            override: If True, replaces any existing registration.
        """
        self.container.register_singleton(
            service_type,
            implementation,
            factory=factory,
            instance=instance,
            override=override,
        )
        self._record(
            service_type,
            ServiceLifetime.SINGLETON,
            description=description,
            registered_by=registered_by,
        )

    def register_transient(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        description: str = "",
        registered_by: str | None = None,
        override: bool = False,
    ) -> None:
        """Register a transient-lifetime service and record its metadata.

        Args:
            service_type: The type other code will resolve by.
            implementation: A concrete class to construct via constructor
                injection.
            factory: A callable taking the container and returning an
                instance.
            description: A human-readable description of the service.
            registered_by: The name of the module or component
                registering this service.
            override: If True, replaces any existing registration.
        """
        self.container.register_transient(
            service_type, implementation, factory=factory, override=override
        )
        self._record(
            service_type,
            ServiceLifetime.TRANSIENT,
            description=description,
            registered_by=registered_by,
        )

    def register_scoped(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        description: str = "",
        registered_by: str | None = None,
        override: bool = False,
    ) -> None:
        """Register a scoped-lifetime service and record its metadata.

        Args:
            service_type: The type other code will resolve by.
            implementation: A concrete class to construct via constructor
                injection.
            factory: A callable taking the container and returning an
                instance.
            description: A human-readable description of the service.
            registered_by: The name of the module or component
                registering this service.
            override: If True, replaces any existing registration.
        """
        self.container.register_scoped(
            service_type, implementation, factory=factory, override=override
        )
        self._record(
            service_type,
            ServiceLifetime.SCOPED,
            description=description,
            registered_by=registered_by,
        )

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service instance by type.

        Args:
            service_type: The type to resolve.

        Returns:
            An instance of ``service_type``.

        Raises:
            quant_os.kernel.exceptions.ServiceNotRegisteredError: If
                ``service_type`` has no registration.
            quant_os.kernel.exceptions.CircularDependencyError: If
                resolving ``service_type`` requires resolving itself.
        """
        return self.container.resolve(service_type)

    def exists(self, service_type: type) -> bool:
        """Check whether a service type is registered.

        Args:
            service_type: The type to check.

        Returns:
            True if registered, False otherwise.
        """
        return self.container.is_registered(service_type)

    def remove(self, service_type: type) -> None:
        """Remove a service registration and its metadata.

        Args:
            service_type: The type to remove. Removing an unregistered
                type is a no-op.
        """
        self.container.unregister(service_type)
        self._metadata.pop(service_type, None)

    def override(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[Container], T] | None = None,
        instance: T | None = None,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
        description: str = "",
        registered_by: str | None = None,
    ) -> None:
        """Replace an existing (or add a new) registration for ``service_type``.

        Args:
            service_type: The type to override.
            implementation: A concrete class to construct via constructor
                injection.
            factory: A callable taking the container and returning an
                instance.
            instance: A pre-built instance to use directly.
            lifetime: The lifetime to register the replacement under.
            description: A human-readable description of the service.
            registered_by: The name of the module or component
                registering this service.
        """
        self.container.replace(
            service_type, implementation, factory=factory, instance=instance, lifetime=lifetime
        )
        self._record(service_type, lifetime, description=description, registered_by=registered_by)

    def list_services(self) -> list[ServiceMetadata]:
        """List metadata for every currently registered service.

        Returns:
            All registered services' metadata.
        """
        return list(self._metadata.values())

    def get_metadata(self, service_type: type) -> ServiceMetadata:
        """Get metadata for a specific registered service.

        Args:
            service_type: The type to look up.

        Returns:
            The service's :class:`ServiceMetadata`.

        Raises:
            quant_os.kernel.exceptions.ServiceNotRegisteredError: If
                ``service_type`` has no registration.
        """
        metadata = self._metadata.get(service_type)
        if metadata is None:
            raise ServiceNotRegisteredError(
                f"No registration found for {service_type.__name__}",
                context={"service_type": service_type.__name__},
            )
        return metadata

    def _record(
        self,
        service_type: type,
        lifetime: ServiceLifetime,
        *,
        description: str,
        registered_by: str | None,
    ) -> None:
        self._metadata[service_type] = ServiceMetadata(
            name=service_type.__qualname__,
            lifetime=lifetime,
            description=description,
            registered_by=registered_by,
        )
