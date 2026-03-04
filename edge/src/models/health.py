"""Health and metrics data models for edge device monitoring."""

from dataclasses import dataclass, asdict


@dataclass
class SensorHealthReport:
    sensor_id: str
    type: str
    room_id: str
    room_number: str
    status: str  # 'online'|'degraded'|'offline'
    last_heartbeat: str
    inference_latency_ms: int
    baseline_latency_ms: int
    uptime: float
    firmware_version: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SystemMetricsReport:
    cpu_usage: float
    memory_usage: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    ntp_drift_ms: int = 0
    ntp_sync_status: str = "synced"
    last_self_test_at: str | None = None
    self_test_passed: bool = True
    edge_device_uptime: str = "0d 0h 0m"

    def to_dict(self) -> dict:
        return asdict(self)
