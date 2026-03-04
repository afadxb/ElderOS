from src.schemas.common import CamelModel


class DeviceResponse(CamelModel):
    id: str
    room_id: str
    room_number: str | None
    type: str | None
    name: str | None
    status: str
    enabled: bool
    edge_device_id: str | None
    last_heartbeat: str | None
    inference_latency_ms: int
    baseline_latency_ms: int
    uptime: float
    firmware_version: str
    connection_config: dict | None = None
    detection_config: dict | None = None


class CreateDeviceRequest(CamelModel):
    room_id: str
    room_number: str | None = None
    type: str
    name: str | None = None
    edge_device_id: str | None = None
    enabled: bool = True
    connection_config: dict | None = None
    detection_config: dict | None = None


class UpdateDeviceRequest(CamelModel):
    room_id: str | None = None
    room_number: str | None = None
    type: str | None = None
    name: str | None = None
    edge_device_id: str | None = None
    enabled: bool | None = None
    connection_config: dict | None = None
    detection_config: dict | None = None


class EdgeDeviceConfig(CamelModel):
    sensor_id: str
    room_id: str
    room_number: str | None
    type: str | None
    name: str | None
    connection_config: dict | None = None
    detection_config: dict | None = None


class EdgeConfigResponse(CamelModel):
    edge_device_id: str
    devices: list[EdgeDeviceConfig]
