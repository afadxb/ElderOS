from src.schemas.common import CamelModel


class CallBellEventResponse(CamelModel):
    id: str
    room_id: str
    room_number: str
    resident_id: str
    resident_name: str
    unit: str
    floor: int
    origin: str
    priority: str
    status: str
    vendor: str
    pressed_at: str
    responded_at: str | None
    closed_at: str | None
    response_time_seconds: int | None
    responded_by: str | None
    responded_by_name: str | None
    shift: str


class CallBellRespondRequest(CamelModel):
    user_id: str
    user_name: str


class CallBellStaffMetricsResponse(CamelModel):
    staff_id: str
    staff_name: str
    role: str
    total_calls: int
    avg_response_seconds: float
    median_response_seconds: float
    min_response_seconds: float
    max_response_seconds: float
    calls_under_60s: int
    calls_under_120s: int
    calls_over_180s: int


class CallBellFloorMetricsResponse(CamelModel):
    floor: int
    unit: str
    total_calls: int
    avg_response_seconds: float
    calls_by_priority: dict[str, int]
    calls_by_origin: dict[str, int]
    peak_hour: int


class CallBellShiftMetricsResponse(CamelModel):
    shift: str
    date: str
    unit: str
    total_calls: int
    avg_response_seconds: float
    responded_within_60s: int
    responded_within_120s: int
    slow_responses: int


class CallBellDailySummaryResponse(CamelModel):
    date: str
    total_calls: int
    avg_response_seconds: float
