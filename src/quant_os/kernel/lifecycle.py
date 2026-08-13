"""Module lifecycle: state vocabulary and the manager enforcing valid transitions."""

from __future__ import annotations

from enum import StrEnum

from quant_os.core.logging import get_logger
from quant_os.kernel.exceptions import ModuleLifecycleError

_logger = get_logger(__name__)


class ModuleState(StrEnum):
    """The lifecycle state of a module, managed by :class:`LifecycleManager`."""

    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SHUTTING_DOWN = "shutting_down"
    DISPOSED = "disposed"
    FAILED = "failed"


_ALLOWED_TRANSITIONS: dict[ModuleState, frozenset[ModuleState]] = {
    ModuleState.CREATED: frozenset({ModuleState.INITIALIZING}),
    ModuleState.INITIALIZING: frozenset({ModuleState.INITIALIZED, ModuleState.FAILED}),
    ModuleState.INITIALIZED: frozenset({ModuleState.STARTING}),
    ModuleState.STARTING: frozenset({ModuleState.READY, ModuleState.FAILED}),
    ModuleState.READY: frozenset({ModuleState.STOPPING, ModuleState.FAILED}),
    ModuleState.STOPPING: frozenset({ModuleState.STOPPED, ModuleState.FAILED}),
    ModuleState.STOPPED: frozenset({ModuleState.STARTING, ModuleState.SHUTTING_DOWN}),
    ModuleState.SHUTTING_DOWN: frozenset({ModuleState.DISPOSED, ModuleState.FAILED}),
    ModuleState.DISPOSED: frozenset(),
    ModuleState.FAILED: frozenset({ModuleState.INITIALIZING, ModuleState.SHUTTING_DOWN}),
}
"""The allowed next states for each state.

Restart is modeled as ``STOPPED -> STARTING`` (resume without
re-initializing) or ``FAILED -> INITIALIZING`` (full re-initialization
after a failure).
"""


class LifecycleManager:
    """Tracks and validates module lifecycle state transitions.

    One :class:`LifecycleManager` is shared across all modules registered
    with an :class:`~quant_os.kernel.application.Application`; each module
    is tracked independently by name.
    """

    def __init__(self) -> None:
        """Initialize a lifecycle manager with no tracked modules."""
        self._states: dict[str, ModuleState] = {}

    def register(self, module_name: str) -> None:
        """Begin tracking a module, starting in :data:`ModuleState.CREATED`.

        Args:
            module_name: The unique name of the module to track.
        """
        self._states[module_name] = ModuleState.CREATED
        _logger.debug(
            "Registered module in lifecycle manager",
            extra={"module_name": module_name, "state": ModuleState.CREATED.value},
        )

    def get_state(self, module_name: str) -> ModuleState:
        """Get the current lifecycle state of a tracked module.

        Args:
            module_name: The module name to look up.

        Returns:
            The module's current state.

        Raises:
            ModuleLifecycleError: If ``module_name`` is not tracked.
        """
        if module_name not in self._states:
            raise ModuleLifecycleError(
                f"Module {module_name!r} is not tracked by the lifecycle manager",
                context={"module": module_name},
            )
        return self._states[module_name]

    def transition(self, module_name: str, new_state: ModuleState) -> None:
        """Transition a tracked module to a new state.

        Args:
            module_name: The module name to transition.
            new_state: The state to transition to.

        Raises:
            ModuleLifecycleError: If ``module_name`` is not tracked, or if
                the transition from its current state to ``new_state`` is
                not permitted.
        """
        current_state = self.get_state(module_name)
        allowed = _ALLOWED_TRANSITIONS[current_state]
        if new_state not in allowed:
            raise ModuleLifecycleError(
                f"Invalid transition for module {module_name!r}: "
                f"{current_state.value} -> {new_state.value}",
                context={
                    "module": module_name,
                    "from_state": current_state.value,
                    "to_state": new_state.value,
                    "allowed": [state.value for state in allowed],
                },
            )
        self._states[module_name] = new_state
        _logger.info(
            "Module lifecycle transition",
            extra={
                "module_name": module_name,
                "from_state": current_state.value,
                "to_state": new_state.value,
            },
        )
