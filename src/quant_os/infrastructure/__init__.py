"""Integrations with external systems: brokers, data vendors, storage, messaging.

Currently exposes the :class:`~quant_os.infrastructure.scheduler.Scheduler`
interface (Milestone 3). No concrete integrations have been implemented
yet.
"""

from quant_os.infrastructure.scheduler import ScheduledCallback, ScheduleHandle, Scheduler

__all__ = ["ScheduleHandle", "ScheduledCallback", "Scheduler"]
