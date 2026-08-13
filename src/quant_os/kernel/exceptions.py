"""Kernel-specific exceptions.

All kernel errors derive from :class:`KernelError`, itself a specialization
of :class:`~quant_os.core.exceptions.InfrastructureError` — kernel failures
are infrastructure-level, not domain/business failures.
"""

from __future__ import annotations

from quant_os.core.exceptions import InfrastructureError


class KernelError(InfrastructureError):
    """Base class for all kernel-level errors."""


class ServiceNotRegisteredError(KernelError):
    """Raised when resolving a service type that has no registration."""


class DuplicateRegistrationError(KernelError):
    """Raised when registering a service type that is already registered
    without explicitly requesting an override.
    """


class CircularDependencyError(KernelError):
    """Raised when a dependency graph contains a cycle."""


class InvalidRegistrationError(KernelError):
    """Raised when a service registration is structurally invalid
    (e.g. neither an implementation type, factory, nor instance given).
    """


class ModuleLifecycleError(KernelError):
    """Raised when a module undergoes an invalid lifecycle state transition."""


class ModuleDependencyError(KernelError):
    """Raised when a module declares a dependency that cannot be satisfied,
    or when module dependencies form a cycle.
    """


class StartupError(KernelError):
    """Raised when application or module startup fails."""


class ShutdownError(KernelError):
    """Raised when application or module shutdown fails.

    May aggregate multiple underlying failures via ``context``, since
    shutdown continues attempting to stop all modules even if one fails.
    """


class HealthCheckError(KernelError):
    """Raised when a health check itself fails to execute (as opposed to
    reporting an unhealthy status).
    """
