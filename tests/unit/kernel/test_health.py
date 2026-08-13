"""Unit tests for the health monitoring system."""

from __future__ import annotations

from quant_os.kernel.health import (
    HealthAggregator,
    HealthCheckable,
    HealthCheckResult,
    HealthReport,
    HealthStatus,
)


class _HealthyComponent:
    async def check_health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY)


class _DegradedComponent:
    async def check_health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.DEGRADED, message="slow")


class _FailingComponent:
    async def check_health(self) -> HealthCheckResult:
        raise RuntimeError("boom")


class TestHealthCheckResult:
    def test_defaults(self) -> None:
        result = HealthCheckResult(status=HealthStatus.HEALTHY)
        assert result.message == ""
        assert result.details == {}
        assert result.checked_at.tzinfo is not None


class TestHealthCheckableProtocol:
    def test_conforming_object_satisfies_protocol(self) -> None:
        assert isinstance(_HealthyComponent(), HealthCheckable)

    def test_non_conforming_object_does_not_satisfy_protocol(self) -> None:
        class NotHealthCheckable:
            pass

        assert not isinstance(NotHealthCheckable(), HealthCheckable)


class TestHealthReportOverallStatus:
    def test_empty_report_is_unknown(self) -> None:
        report = HealthReport(results={})
        assert report.overall_status == HealthStatus.UNKNOWN

    def test_all_healthy_is_healthy(self) -> None:
        report = HealthReport(
            results={
                "a": HealthCheckResult(status=HealthStatus.HEALTHY),
                "b": HealthCheckResult(status=HealthStatus.HEALTHY),
            }
        )
        assert report.overall_status == HealthStatus.HEALTHY

    def test_worst_status_wins(self) -> None:
        report = HealthReport(
            results={
                "a": HealthCheckResult(status=HealthStatus.HEALTHY),
                "b": HealthCheckResult(status=HealthStatus.UNAVAILABLE),
                "c": HealthCheckResult(status=HealthStatus.DEGRADED),
            }
        )
        assert report.overall_status == HealthStatus.UNAVAILABLE

    def test_degraded_worse_than_unknown(self) -> None:
        report = HealthReport(
            results={
                "a": HealthCheckResult(status=HealthStatus.UNKNOWN),
                "b": HealthCheckResult(status=HealthStatus.DEGRADED),
            }
        )
        assert report.overall_status == HealthStatus.DEGRADED


class TestHealthAggregator:
    async def test_aggregates_multiple_components(self) -> None:
        aggregator = HealthAggregator()
        report = await aggregator.check_all(
            {"healthy": _HealthyComponent(), "degraded": _DegradedComponent()}
        )
        assert report.results["healthy"].status == HealthStatus.HEALTHY
        assert report.results["degraded"].status == HealthStatus.DEGRADED
        assert report.overall_status == HealthStatus.DEGRADED

    async def test_failing_check_reported_as_unavailable(self) -> None:
        aggregator = HealthAggregator()
        report = await aggregator.check_all({"failing": _FailingComponent()})
        assert report.results["failing"].status == HealthStatus.UNAVAILABLE
        assert "boom" in report.results["failing"].message

    async def test_empty_components_returns_empty_report(self) -> None:
        aggregator = HealthAggregator()
        report = await aggregator.check_all({})
        assert report.results == {}
        assert report.overall_status == HealthStatus.UNKNOWN
