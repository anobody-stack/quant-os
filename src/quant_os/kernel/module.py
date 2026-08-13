"""The Module abstraction every QuantOS module plugs into the kernel through."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field

from quant_os.core.types import Version
from quant_os.kernel.capabilities import Capability
from quant_os.kernel.health import HealthCheckResult, HealthStatus


class ModuleMetadata(BaseModel):
    """Static, self-describing information about a module.

    Attributes:
        name: A unique, stable identifier for the module (e.g. ``"news"``).
        version: The module's own version.
        description: A short human-readable description of the module.
        dependencies: Names of other modules that must be initialized
            before this one.
        capabilities: The capabilities this module advertises.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    version: Version
    description: str
    dependencies: tuple[str, ...] = Field(default_factory=tuple)
    capabilities: tuple[Capability, ...] = Field(default_factory=tuple)


class Module(ABC):
    """Base class every QuantOS module must implement to plug into the kernel.

    Configuration and other dependencies are provided via constructor
    injection (resolved by the :class:`~quant_os.kernel.container.Container`)
    — modules should never load environment variables or configuration
    directly.

    Lifecycle hooks default to no-ops so subclasses only need to override
    the ones relevant to them; :meth:`check_health` defaults to reporting
    :data:`~quant_os.kernel.health.HealthStatus.UNKNOWN`.
    """

    @property
    @abstractmethod
    def metadata(self) -> ModuleMetadata:
        """This module's static metadata.

        Returns:
            The module's :class:`ModuleMetadata`.
        """
        raise NotImplementedError

    async def on_initialize(self) -> None:
        """Called once, before :meth:`on_start`, to prepare the module.

        The default implementation does nothing. Override to perform
        setup that must happen before the module is considered
        initialized (e.g. validating configuration).
        """
        return None

    async def on_start(self) -> None:
        """Called to start the module after initialization.

        The default implementation does nothing. Override to begin any
        ongoing work (e.g. opening connections, starting background
        tasks).
        """
        return None

    async def on_stop(self) -> None:
        """Called to stop the module's ongoing work.

        The default implementation does nothing. Override to gracefully
        halt work started in :meth:`on_start`.
        """
        return None

    async def on_dispose(self) -> None:
        """Called to release any resources held by the module.

        The default implementation does nothing. Override to release
        resources that outlive a single start/stop cycle.
        """
        return None

    async def check_health(self) -> HealthCheckResult:
        """Report this module's current health.

        The default implementation reports
        :data:`~quant_os.kernel.health.HealthStatus.UNKNOWN`. Override to
        provide a meaningful health signal.

        Returns:
            The module's current :class:`~quant_os.kernel.health.HealthCheckResult`.
        """
        return HealthCheckResult(status=HealthStatus.UNKNOWN)
