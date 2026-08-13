"""Health monitoring: status vocabulary, results, and aggregation."""

from __future__ import annotations

import asyncio
from datetime import datetime
from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from quant_os.core.time import utc_now


class HealthStatus(StrEnum):
    """The health of a module or the application as a whole.

    Ordered from best to worst via :data:`_SEVERITY` for aggregation
    purposes.
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


_SEVERITY: dict[HealthStatus, int] = {
    HealthStatus.HEALTHY: 0,
    HealthStatus.UNKNOWN: 1,
    HealthStatus.DEGRADED: 2,
    HealthStatus.UNAVAILABLE: 3,
}


class HealthCheckResult(BaseModel):
    """The result of a single health check.

    Attributes:
        status: The reported health status.
        message: A short human-readable explanation.
        checked_at: UTC time the check was performed.
        details: Arbitrary structured diagnostic details.
    """

    model_config = ConfigDict(frozen=True)

    status: HealthStatus
    message: str = ""
    checked_at: datetime = Field(default_factory=utc_now)
    details: dict[str, str] = Field(default_factory=dict)


@runtime_checkable
class HealthCheckable(Protocol):
    """Anything that can report its own health."""

    async def check_health(self) -> HealthCheckResult:
        """Report the current health of this component.

        Returns:
            The current :class:`HealthCheckResult`.
        """
        ...


class HealthReport(BaseModel):
    """An aggregated health report across multiple named components.

    Attributes:
        results: Per-component health check results, keyed by component
            name.
    """

    model_config = ConfigDict(frozen=True)

    results: dict[str, HealthCheckResult]

    @property
    def overall_status(self) -> HealthStatus:
        """The worst status among all component results.

        Returns:
            :data:`HealthStatus.UNKNOWN` if there are no results, otherwise
            the most severe status present (severity order: HEALTHY <
            UNKNOWN < DEGRADED < UNAVAILABLE).
        """
        if not self.results:
            return HealthStatus.UNKNOWN
        return max(
            (result.status for result in self.results.values()),
            key=lambda status: _SEVERITY[status],
        )


class HealthAggregator:
    """Runs health checks across multiple components and aggregates the results."""

    async def check_all(self, components: dict[str, HealthCheckable]) -> HealthReport:
        """Run health checks concurrently across all given components.

        A component whose check raises an exception is reported as
        :data:`HealthStatus.UNAVAILABLE` rather than propagating the
        exception, so that one failing check cannot prevent reporting on
        the others.

        Args:
            components: Components to check, keyed by name.

        Returns:
            The aggregated :class:`HealthReport`.
        """
        names = list(components)
        outcomes = await asyncio.gather(
            *(components[name].check_health() for name in names), return_exceptions=True
        )
        results: dict[str, HealthCheckResult] = {}
        for name, outcome in zip(names, outcomes, strict=True):
            if isinstance(outcome, BaseException):
                results[name] = HealthCheckResult(
                    status=HealthStatus.UNAVAILABLE,
                    message=str(outcome),
                )
            else:
                results[name] = outcome
        return HealthReport(results=results)
