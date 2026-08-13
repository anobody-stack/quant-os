"""Scheduler abstraction.

This is an interface only — no concrete scheduling mechanism (cron,
APScheduler, timers, etc.) is implemented here. That is reserved for a
later milestone.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

from quant_os.core.identifiers import TypedId

ScheduledCallback = Callable[[], Awaitable[None]]
"""An async callable with no arguments, invoked when a schedule fires."""


class ScheduleHandle(TypedId):
    """Opaque identifier for a scheduled job, returned by ``schedule()``."""


@runtime_checkable
class Scheduler(Protocol):
    """Abstraction for scheduling recurring or future work.

    Concrete implementations may support polling, streaming, periodic
    updates, calendar synchronization, market-open/close triggers, or
    arbitrary future scheduled events — none of that timing behavior is
    defined here.
    """

    async def start(self) -> None:
        """Start the scheduler, allowing scheduled callbacks to fire."""
        ...

    async def stop(self) -> None:
        """Stop the scheduler, preventing further callbacks from firing."""
        ...

    def schedule(self, callback: ScheduledCallback) -> ScheduleHandle:
        """Register a callback to be invoked according to the scheduler's policy.

        Args:
            callback: The async, no-argument callable to invoke when the
                schedule fires.

        Returns:
            A handle identifying this scheduled job, usable with
            :meth:`cancel`.
        """
        ...

    def cancel(self, handle: ScheduleHandle) -> None:
        """Cancel a previously scheduled job.

        Args:
            handle: The handle returned by :meth:`schedule`. Canceling an
                unknown or already-canceled handle is a no-op.
        """
        ...
