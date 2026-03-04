"""Tests for health reporting and metrics collection."""

import pytest
from unittest.mock import MagicMock, patch

from src.health.metrics_collector import MetricsCollector
from src.models.health import SystemMetricsReport


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_metrics_collection():
    """MetricsCollector.collect() returns a valid SystemMetricsReport with
    realistic numeric values."""
    # Mock psutil so the test does not depend on real system stats
    mock_disk = MagicMock(percent=42.5, used=50 * (1024**3), total=120 * (1024**3))
    mock_vmem = MagicMock(percent=65.3)

    with (
        patch("src.health.metrics_collector.psutil.cpu_percent", return_value=23.1),
        patch("src.health.metrics_collector.psutil.virtual_memory", return_value=mock_vmem),
        patch("src.health.metrics_collector.psutil.disk_usage", return_value=mock_disk),
    ):
        collector = MetricsCollector()
        report = collector.collect()

    assert isinstance(report, SystemMetricsReport)
    assert report.cpu_usage == 23.1
    assert report.memory_usage == 65.3
    assert report.disk_usage_percent == 42.5
    assert report.disk_used_gb == 50.0
    assert report.disk_total_gb == 120.0
    assert "d" in report.edge_device_uptime  # e.g. "0d 0h 0m"
    assert "h" in report.edge_device_uptime


def test_metrics_report_to_dict():
    """SystemMetricsReport.to_dict() returns a plain dictionary."""
    report = SystemMetricsReport(
        cpu_usage=10.0,
        memory_usage=50.0,
        disk_usage_percent=30.0,
        disk_used_gb=15.0,
        disk_total_gb=50.0,
    )
    d = report.to_dict()
    assert isinstance(d, dict)
    assert d["cpu_usage"] == 10.0
    assert d["ntp_drift_ms"] == 0
    assert d["ntp_sync_status"] == "synced"
    assert d["self_test_passed"] is True
