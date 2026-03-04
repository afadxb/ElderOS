from src.schemas.common import CamelModel


class EdgeSensorHealth(CamelModel):
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


class EdgeEventPayload(CamelModel):
    room_id: str
    room_number: str
    resident_id: str
    resident_name: str
    event_type: str
    severity: str
    confidence: str
    confidence_score: int
    sensor_source: str
    bed_zone: str | None
    pre_event_summary: str
    post_event_state: str
    is_repeat_fall: bool
    detected_at: str


class EdgeCallBellPayload(CamelModel):
    room_id: str
    room_number: str
    resident_id: str
    resident_name: str
    unit: str
    floor: int
    origin: str
    priority: str
    vendor: str
    pressed_at: str


class EdgeHealthPayload(CamelModel):
    sensors: list[EdgeSensorHealth]


class EdgeMetricsPayload(CamelModel):
    cpu_usage: float
    memory_usage: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    ntp_drift_ms: int
    ntp_sync_status: str
    last_self_test_at: str | None
    self_test_passed: bool
    edge_device_uptime: str
