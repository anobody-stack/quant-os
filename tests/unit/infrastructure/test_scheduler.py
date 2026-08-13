"""Structural conformance tests for the Scheduler interface.

The Scheduler has no implementation yet (per Milestone 3 scope), so tests
here verify only that the Protocol is well-formed and correctly detects
structural conformance — not any concrete scheduling behavior.
"""

from __future__ import annotations

from quant_os.core.identifiers import TypedId
from quant_os.infrastructure.scheduler import ScheduledCallback, ScheduleHandle, Scheduler


class _ConformingScheduler:
    """A minimal object satisfying the Scheduler protocol."""

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    def schedule(self, callback: ScheduledCallback) -> ScheduleHandle:
        return ScheduleHandle.generate()

    def cancel(self, handle: ScheduleHandle) -> None:
        return None


class _NonConformingScheduler:
    """An object missing required protocol methods."""


def test_conforming_scheduler_satisfies_protocol() -> None:
    assert isinstance(_ConformingScheduler(), Scheduler)


def test_non_conforming_scheduler_does_not_satisfy_protocol() -> None:
    assert not isinstance(_NonConformingScheduler(), Scheduler)


def test_schedule_handle_is_a_typed_id() -> None:
    handle = ScheduleHandle.generate()
    assert isinstance(handle, TypedId)


def test_schedule_handle_from_string_round_trips() -> None:
    handle = ScheduleHandle.generate()
    restored = ScheduleHandle.from_string(str(handle))
    assert restored == handle
