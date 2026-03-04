from src.schemas.common import CamelModel


class ShiftSummaryResponse(CamelModel):
    shift_id: str
    shift_name: str
    date: str
    start_time: str
    end_time: str
    unit: str
    total_events: int
    falls: int
    bed_exits: int
    inactivity_alerts: int
    unsafe_transfers: int
    avg_ack_time_seconds: float
    avg_resolve_time_seconds: float
    unacknowledged_count: int
    escalated_count: int
    high_risk_residents: list[str]
    notable_incidents: list[str]


class WeeklyDigestResponse(CamelModel):
    week_start: str
    week_end: str
    unit: str
    total_falls: int
    unwitnessed_falls: int
    avg_response_time_seconds: float
    median_response_time_seconds: float
    repeat_fall_residents: list[str]
    compliance_score: int
    trend_vs_prior_week: str


class UnitSummary(CamelModel):
    unit: str
    falls: int
    avg_response_time: float
    unwitnessed_rate: float
    compliance_score: int


class LiabilityIndicators(CamelModel):
    slow_responses: int
    unacknowledged_alerts: int
    repeat_falls: int


class MonthlyTrend(CamelModel):
    month: str
    falls: int
    avg_response_time: float


class BoardReportResponse(CamelModel):
    period: str
    facility_name: str
    unit_summaries: list[UnitSummary]
    liability_indicators: LiabilityIndicators
    trends_monthly: list[MonthlyTrend]
