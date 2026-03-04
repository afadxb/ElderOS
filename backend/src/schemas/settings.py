from src.schemas.common import CamelModel


class EscalationRuleResponse(CamelModel):
    id: str
    delay_minutes: int
    action: str
    target: str
    enabled: bool


class EscalationRuleUpdate(CamelModel):
    id: str
    delay_minutes: int
    action: str
    target: str
    enabled: bool


class ConfidenceThresholdsResponse(CamelModel):
    high_min: int
    medium_min: int
    low_min: int


class ConfidenceThresholdsUpdate(CamelModel):
    high_min: int
    medium_min: int
    low_min: int


class RetentionPolicyResponse(CamelModel):
    clip_retention_days: int
    metadata_retention_days: int
    auto_purge_enabled: bool
    purge_threshold_percent: int


class RetentionPolicyUpdate(CamelModel):
    clip_retention_days: int
    metadata_retention_days: int
    auto_purge_enabled: bool
    purge_threshold_percent: int


class ExclusionZoneResponse(CamelModel):
    id: str
    room_id: str
    room_number: str
    zone_name: str
    enabled: bool


class ExclusionZoneUpdate(CamelModel):
    id: str
    room_id: str
    room_number: str
    zone_name: str
    enabled: bool
