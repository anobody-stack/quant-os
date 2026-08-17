"""The Application: bootstraps the kernel and orchestrates module lifecycle."""

from __future__ import annotations

from quant_os.core.logging import get_logger
from quant_os.kernel.bootstrap import build_container
from quant_os.kernel.container import Container
from quant_os.kernel.exceptions import (
    ModuleDependencyError,
    ShutdownError,
    StartupError,
)
from quant_os.kernel.health import HealthAggregator, HealthReport
from quant_os.kernel.lifecycle import LifecycleManager, ModuleState
from quant_os.kernel.module import Module
from quant_os.kernel.registry import ServiceRegistry

_logger = get_logger(__name__)


class Application:
    """Orchestrates the QuantOS kernel: modules, lifecycle, and health.

    Typical usage:

    .. code-block:: python

        app = Application()
        app.register_module(SomeModule())
        await app.initialize()
        await app.start()
        report = await app.run_health_checks()
        await app.shutdown()
    """

    def __init__(self, container: Container | None = None) -> None:
        """Initialize the application.

        Args:
            container: The container to use. A fresh, fully bootstrapped
                container is created via
                :func:`~quant_os.kernel.bootstrap.build_container` when not
                provided.
        """
        self.container = container if container is not None else build_container()
        self.registry = ServiceRegistry(self.container)
        self.lifecycle = self.container.resolve(LifecycleManager)
        self.health_aggregator = self.container.resolve(HealthAggregator)
        self._modules: dict[str, Module] = {}

    def register_module(self, module: Module) -> None:
        """Register a module with the application.

        Args:
            module: The module instance to register.

        Raises:
            ModuleDependencyError: If a module with the same name is
                already registered, or if a declared dependency has not
                itself been registered.
        """
        name = module.metadata.name
        if name in self._modules:
            raise ModuleDependencyError(
                f"Module {name!r} is already registered", context={"module": name}
            )
        for dependency in module.metadata.dependencies:
            if dependency not in self._modules:
                raise ModuleDependencyError(
                    f"Module {name!r} depends on {dependency!r}, which has not been registered",
                    context={"module": name, "dependency": dependency},
                )
        self._modules[name] = module
        self.lifecycle.register(name)
        _logger.info(
            "Module registered",
            extra={"module_name": name, "version": str(module.metadata.version)},
        )

    def get_module(self, name: str) -> Module:
        """Retrieve a registered module by name.

        Args:
            name: The module's name.

        Returns:
            The registered :class:`~quant_os.kernel.module.Module`.

        Raises:
            ModuleDependencyError: If no module named ``name`` is
                registered.
        """
        module = self._modules.get(name)
        if module is None:
            raise ModuleDependencyError(f"No module named {name!r} is registered")
        return module

    def _ordered_module_names(self) -> list[str]:
        """Topologically sort registered modules by declared dependencies.

        Returns:
            Module names ordered so that every module appears after all
            of its dependencies.

        Raises:
            ModuleDependencyError: If the dependency graph contains a
                cycle.
        """
        visited: set[str] = set()
        visiting: set[str] = set()
        order: list[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                raise ModuleDependencyError(
                    f"Circular module dependency detected involving {name!r}",
                    context={"module": name},
                )
            visiting.add(name)
            for dependency in self._modules[name].metadata.dependencies:
                visit(dependency)
            visiting.discard(name)
            visited.add(name)
            order.append(name)

        for module_name in self._modules:
            visit(module_name)
        return order

    async def initialize(self) -> None:
        """Initialize all registered modules, in dependency order.

        Raises:
            StartupError: If any module's
                :meth:`~quant_os.kernel.module.Module.on_initialize` raises.
                The module is marked
                :data:`~quant_os.kernel.lifecycle.ModuleState.FAILED` and
                initialization stops immediately (subsequent modules are
                not initialized).
        """
        for name in self._ordered_module_names():
            module = self._modules[name]
            self.lifecycle.transition(name, ModuleState.INITIALIZING)
            try:
                await module.on_initialize()
            except Exception as exc:
                self.lifecycle.transition(name, ModuleState.FAILED)
                raise StartupError(
                    f"Module {name!r} failed to initialize",
                    cause=exc,
                    context={"module": name},
                ) from exc
            self.lifecycle.transition(name, ModuleState.INITIALIZED)
            _logger.info("Module initialized", extra={"module_name": name})

    async def start(self) -> None:
        """Start all registered modules, in dependency order.

        Raises:
            StartupError: If any module's
                :meth:`~quant_os.kernel.module.Module.on_start` raises. The
                module is marked
                :data:`~quant_os.kernel.lifecycle.ModuleState.FAILED` and
                startup stops immediately (subsequent modules are not
                started).
        """
        for name in self._ordered_module_names():
            module = self._modules[name]
            self.lifecycle.transition(name, ModuleState.STARTING)
            try:
                await module.on_start()
            except Exception as exc:
                self.lifecycle.transition(name, ModuleState.FAILED)
                raise StartupError(
                    f"Module {name!r} failed to start", cause=exc, context={"module": name}
                ) from exc
            self.lifecycle.transition(name, ModuleState.READY)
            _logger.info("Module started", extra={"module_name": name})

    async def run_health_checks(self) -> HealthReport:
        """Run health checks across all registered modules.

        Returns:
            The aggregated :class:`~quant_os.kernel.health.HealthReport`.
        """
        return await self.health_aggregator.check_all(dict(self._modules))

    async def shutdown(self) -> None:
        """Stop and dispose all registered modules, in reverse dependency order.

        Shutdown is best-effort: a failure stopping or disposing one
        module does not prevent attempting to shut down the others. All
        failures are collected and raised together at the end.

        Raises:
            ShutdownError: If one or more modules failed to stop or
                dispose. The exception's context includes the number of
                failures; each failure is also logged individually.
        """
        failures: list[tuple[str, Exception]] = []
        for name in reversed(self._ordered_module_names()):
            module = self._modules[name]
            current_state = self.lifecycle.get_state(name)
            if current_state not in (ModuleState.READY, ModuleState.STOPPED):
                continue
            try:
                if current_state is ModuleState.READY:
                    self.lifecycle.transition(name, ModuleState.STOPPING)
                    await module.on_stop()
                    self.lifecycle.transition(name, ModuleState.STOPPED)
                self.lifecycle.transition(name, ModuleState.SHUTTING_DOWN)
                await module.on_dispose()
                self.lifecycle.transition(name, ModuleState.DISPOSED)
                _logger.info("Module shut down", extra={"module_name": name})
            except Exception as exc:
                self.lifecycle.transition(name, ModuleState.FAILED)
                failures.append((name, exc))
                _logger.error(
                    "Module failed to shut down", extra={"module_name": name, "error": str(exc)}
                )

        if failures:
            raise ShutdownError(
                f"{len(failures)} module(s) failed to shut down cleanly",
                cause=failures[0][1],
                context={
                    "failed_modules": [name for name, _ in failures],
                    "failure_count": len(failures),
                },
            )
