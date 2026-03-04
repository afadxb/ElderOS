from src.schemas.common import CamelModel


class RoomResidentResponse(CamelModel):
    resident_id: str
    resident_name: str
    bed_zone: str | None


class SensorStatusResponse(CamelModel):
    id: str
    type: str
    online: bool
    last_heartbeat: str
    health_score: int


class BedZoneResponse(CamelModel):
    room_id: str
    label: str
    vertices: list[list[float]]


class BedZoneUpdate(CamelModel):
    label: str = "bed"
    vertices: list[list[float]]


class RoomResponse(CamelModel):
    id: str
    number: str
    unit: str
    floor: int
    room_type: str
    sensor_type: str
    status: str
    status_color: str
    residents: list[RoomResidentResponse]
    sensors: list[SensorStatusResponse]
    last_event_at: str | None
    has_exclusion_zone: bool
    bed_zone_vertices: list[list[float]] | None = None
