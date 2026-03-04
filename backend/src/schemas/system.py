from src.schemas.common import CamelModel


class SensorHealthResponse(CamelModel):
    sensor_id: str
    type: str
    room_id: str
    room_number: str
    status: str
    last_heartbeat: str
    inference_latency_ms: int
    baseline_latency_ms: int
    uptime: float
    firmware_version: str


class SystemMetricsResponse(CamelModel):
    cpu_usage: float
    memory_usage: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    retention_days: int
    auto_purge_threshold_percent: int
    ntp_drift_ms: int
    ntp_sync_status: str
    last_self_test_at: str | None
    self_test_passed: bool
    edge_device_uptime: str


class SelfTestResponse(CamelModel):
    passed: bool
    details: list[str]
