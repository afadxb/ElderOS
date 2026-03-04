from src.schemas.common import CamelModel


class EscalationStepResponse(CamelModel):
    level: int
    action: str
    triggered_at: str
    acknowledged: bool


class IncidentResponse(CamelModel):
    id: str
    event_id: str
    room_number: str
    resident_name: str
    resident_id: str
    event_type: str
    confidence: str
    confidence_score: int
    status: str
    ntp_timestamp: str
    detected_at: str
    acknowledged_at: str | None
    resolved_at: str | None
    ack_response_seconds: int | None
    resolve_response_seconds: int | None
    acknowledged_by: str | None
    resolved_by: str | None
    pre_event_summary: str
    post_event_state: str
    is_repeat_fall: bool
    notes: str
    unit: str
    sensor_source: str
    bed_zone: str | None
    escalation_timeline: list[EscalationStepResponse]
