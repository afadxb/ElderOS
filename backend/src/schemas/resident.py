from pydantic import Field

from src.schemas.common import CamelModel


class ResidentResponse(CamelModel):
    id: str
    name: str
    room_id: str
    room_number: str
    unit: str
    bed_zone: str | None
    age: int
    risk_score: int
    risk_trend: str
    fall_count_30_days: int = Field(validation_alias="fall_count_30d")
    fall_count_total: int
    last_fall_date: str | None
    last_event_date: str | None
    admitted_at: str
    observe_only: bool
