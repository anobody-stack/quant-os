"""The QuantOS Application Kernel.

The kernel is the operating-system layer every future QuantOS module
(market data, news, macro, risk, portfolio, execution, AI, reporting)
plugs into. It provides dependency injection, service registration,
module registration, lifecycle management, health monitoring,
configuration binding, and application bootstrapping.

This package contains no domain-specific logic.
"""

from quant_os.kernel.application import Application
from quant_os.kernel.bootstrap import build_container
from quant_os.kernel.capabilities import Capability
from quant_os.kernel.container import Container, Scope
from quant_os.kernel.exceptions import (
    CircularDependencyError,
    DuplicateRegistrationError,
    HealthCheckError,
    InvalidRegistrationError,
    KernelError,
    ModuleDependencyError,
    ModuleLifecycleError,
    ServiceNotRegisteredError,
    ShutdownError,
    StartupError,
)
from quant_os.kernel.health import (
    HealthAggregator,
    HealthCheckable,
    HealthCheckResult,
    HealthReport,
    HealthStatus,
)
from quant_os.kernel.lifecycle import LifecycleManager, ModuleState
from quant_os.kernel.module import Module, ModuleMetadata
from quant_os.kernel.plugin import Plugin, PluginManager, PluginMetadata
from quant_os.kernel.registry import ServiceMetadata, ServiceRegistry
from quant_os.kernel.service import ServiceDescriptor, ServiceLifetime

__all__ = [
    "Application",
    "Capability",
    "CircularDependencyError",
    "Container",
    "DuplicateRegistrationError",
    "HealthAggregator",
    "HealthCheckError",
    "HealthCheckResult",
    "HealthCheckable",
    "HealthReport",
    "HealthStatus",
    "InvalidRegistrationError",
    "KernelError",
    "LifecycleManager",
    "Module",
    "ModuleDependencyError",
    "ModuleLifecycleError",
    "ModuleMetadata",
    "ModuleState",
    "Plugin",
    "PluginManager",
    "PluginMetadata",
    "Scope",
    "ServiceDescriptor",
    "ServiceLifetime",
    "ServiceMetadata",
    "ServiceNotRegisteredError",
    "ServiceRegistry",
    "ShutdownError",
    "StartupError",
    "build_container",
]
