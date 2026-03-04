"""Event data models emitted by the edge appliance."""

from dataclasses import dataclass, asdict


@dataclass
class EdgeEvent:
    room_id: str
    room_number: str
    resident_id: str
    resident_name: str
    event_type: str  # 'fall'|'bed-exit'|'inactivity'|'unsafe-transfer'
    severity: str  # 'critical'|'warning'
    confidence: str  # 'high'|'medium'|'low'
    confidence_score: int
    sensor_source: str  # 'ai-vision'|'ai-sensor'|'fused'
    bed_zone: str | None
    pre_event_summary: str
    post_event_state: str
    is_repeat_fall: bool
    detected_at: str  # ISO 8601
    unit: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CallBellPayload:
    room_id: str
    room_number: str
    resident_id: str
    resident_name: str
    unit: str
    floor: int
    origin: str  # 'bedside'|'bathroom'|'hallway'|'pendant'
    priority: str  # 'emergency'|'urgent'|'normal'
    vendor: str
    pressed_at: str

    def to_dict(self) -> dict:
        return asdict(self)
