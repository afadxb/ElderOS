from src.schemas.common import CamelModel


class AlertEventResponse(CamelModel):
    id: str
    room_id: str
    room_number: str
    resident_id: str
    resident_name: str
    event_type: str
    severity: str
    confidence: str
    confidence_score: int
    status: str
    detected_at: str
    acknowledged_at: str | None
    resolved_at: str | None
    acknowledged_by: str | None
    resolved_by: str | None
    escalation_level: int
    pre_event_summary: str
    post_event_state: str
    is_repeat_fall: bool
    unit: str
    sensor_source: str
    bed_zone: str | None


class AcknowledgeRequest(CamelModel):
    user_id: str


class ResolveRequest(CamelModel):
    user_id: str
