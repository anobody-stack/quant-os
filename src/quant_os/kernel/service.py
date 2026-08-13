"""Service lifetime and descriptor primitives used by the DI container."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ServiceLifetime(StrEnum):
    """How long a resolved service instance is retained and reused.

    Attributes:
        SINGLETON: One instance for the lifetime of the container.
        TRANSIENT: A new instance is created on every resolution.
        SCOPED: One instance per :class:`~quant_os.kernel.container.Scope`.
    """

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass(frozen=True, slots=True)
class ServiceDescriptor:
    """Describes how a service type should be constructed and cached.

    Exactly one of ``implementation``, ``factory``, or ``instance`` is
    expected to be set; this is enforced by the container at registration
    time, not by the descriptor itself.

    Attributes:
        service_type: The type (typically an interface or Protocol) other
            code depends on and resolves by.
        lifetime: How instances of this service are cached and reused.
        implementation: A concrete class to construct via constructor
            injection, if provided.
        factory: A callable taking the container and returning an
            instance, if provided.
        instance: A pre-built instance to return directly, if provided.
            Implies :attr:`ServiceLifetime.SINGLETON` semantics.
    """

    service_type: type
    lifetime: ServiceLifetime
    implementation: type | None = None
    factory: Callable[[Any], Any] | None = None
    instance: object | None = None
