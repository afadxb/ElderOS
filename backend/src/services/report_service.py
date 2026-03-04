import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import desc, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event
from src.models.resident import Resident
from src.utils.time_utils import dt_to_iso, get_shift_name, seconds_between


# ---------------------------------------------------------------------------
# Shift summaries
# ---------------------------------------------------------------------------


def _shift_window(d: date, shift_name: str) -> tuple[datetime, datetime]:
    """Return (start, end) datetimes for a shift on a given date."""
    if shift_name == "Day":
        start = datetime(d.year, d.month, d.day, 7, tzinfo=timezone.utc)
        end = datetime(d.year, d.month, d.day, 15, tzinfo=timezone.utc)
    elif shift_name == "Evening":
        start = datetime(d.year, d.month, d.day, 15, tzinfo=timezone.utc)
        end = datetime(d.year, d.month, d.day, 23, tzinfo=timezone.utc)
    else:  # Night
        start = datetime(d.year, d.month, d.day, 23, tzinfo=timezone.utc)
        end = start + timedelta(hours=8)  # next day 07:00
    return start, end


async def get_shift_summaries(
    db: AsyncSession,
    target_date: date | None = None,
    unit: str | None = None,
) -> list[dict]:
    """Build shift summary dicts for Day / Evening / Night on a given date."""
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    shifts = ["Day", "Evening", "Night"]
    summaries: list[dict] = []

    for shift_name in shifts:
        start, end = _shift_window(target_date, shift_name)

        query = select(Event).where(
            Event.detected_at >= start,
            Event.detected_at < end,
        )
        if unit:
            query = query.where(Event.unit == unit)

        result = await db.execute(query)
        events = list(result.scalars().all())

        falls = sum(1 for e in events if e.event_type == "fall")
        bed_exits = sum(1 for e in events if e.event_type == "bed-exit")
        inactivity = sum(1 for e in events if e.event_type == "inactivity")
        unsafe = sum(1 for e in events if e.event_type == "unsafe-transfer")

        ack_times = [
            seconds_between(e.detected_at, e.acknowledged_at)
            for e in events
            if e.acknowledged_at and e.detected_at
        ]
        resolve_times = [
            seconds_between(e.detected_at, e.resolved_at)
            for e in events
            if e.resolved_at and e.detected_at
        ]

        unack = sum(1 for e in events if e.status == "active")
        escalated = sum(1 for e in events if e.status == "escalated")

        # Collect high-risk resident names involved in this shift
        resident_ids = {e.resident_id for e in events if e.resident_id}
        high_risk_names: list[str] = []
        if resident_ids:
            res_result = await db.execute(
                select(Resident).where(
                    Resident.id.in_(resident_ids),
                    Resident.risk_score >= 70,
                )
            )
            high_risk_names = [r.name for r in res_result.scalars().all()]

        notable = [
            f"{e.event_type} in room {e.room_number}"
            for e in events
            if e.severity == "critical" or e.is_repeat_fall
        ]

        summaries.append(
            {
                "shift_id": str(uuid.uuid4()),
                "shift_name": shift_name,
                "date": target_date.isoformat(),
                "start_time": dt_to_iso(start),
                "end_time": dt_to_iso(end),
                "unit": unit or "all",
                "total_events": len(events),
                "falls": falls,
                "bed_exits": bed_exits,
                "inactivity_alerts": inactivity,
                "unsafe_transfers": unsafe,
                "avg_ack_time_seconds": (
                    round(sum(ack_times) / len(ack_times), 1) if ack_times else 0.0
                ),
                "avg_resolve_time_seconds": (
                    round(sum(resolve_times) / len(resolve_times), 1)
                    if resolve_times
                    else 0.0
                ),
                "unacknowledged_count": unack,
                "escalated_count": escalated,
                "high_risk_residents": high_risk_names,
                "notable_incidents": notable,
            }
        )

    return summaries


# ---------------------------------------------------------------------------
# Weekly digest
# ---------------------------------------------------------------------------


async def get_weekly_digest(
    db: AsyncSession, unit: str | None = None
) -> dict:
    """Aggregate the last 7 days into a weekly digest."""
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=7)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_end = now

    query = select(Event).where(Event.detected_at >= week_start)
    if unit:
        query = query.where(Event.unit == unit)

    result = await db.execute(query)
    events = list(result.scalars().all())

    total_falls = sum(1 for e in events if e.event_type == "fall")
    # Unwitnessed = events where confidence is 'medium' or 'low' (no staff present)
    unwitnessed = sum(
        1
        for e in events
        if e.event_type == "fall" and e.confidence in ("medium", "low")
    )

    response_times = [
        seconds_between(e.detected_at, e.acknowledged_at)
        for e in events
        if e.acknowledged_at and e.detected_at
    ]

    avg_response = (
        round(sum(response_times) / len(response_times), 1) if response_times else 0.0
    )
    sorted_times = sorted(response_times)
    median_response = 0.0
    if sorted_times:
        mid = len(sorted_times) // 2
        if len(sorted_times) % 2 == 0:
            median_response = round((sorted_times[mid - 1] + sorted_times[mid]) / 2, 1)
        else:
            median_response = float(sorted_times[mid])

    repeat_fall_names: list[str] = []
    repeat_ids = {e.resident_id for e in events if e.is_repeat_fall and e.resident_id}
    if repeat_ids:
        res_result = await db.execute(
            select(Resident.name).where(Resident.id.in_(repeat_ids))
        )
        repeat_fall_names = list(res_result.scalars().all())

    # Compliance score: % of events acknowledged within 3 minutes
    acked_in_time = sum(1 for t in response_times if t <= 180)
    compliance = int((acked_in_time / len(response_times)) * 100) if response_times else 100

    # Prior week for trend comparison
    prior_start = week_start - timedelta(days=7)
    prior_query = select(Event).where(
        Event.detected_at >= prior_start,
        Event.detected_at < week_start,
    )
    if unit:
        prior_query = prior_query.where(Event.unit == unit)
    prior_result = await db.execute(prior_query)
    prior_events = list(prior_result.scalars().all())
    prior_falls = sum(1 for e in prior_events if e.event_type == "fall")

    if prior_falls == 0:
        trend = "stable"
    elif total_falls < prior_falls:
        trend = "improving"
    elif total_falls > prior_falls:
        trend = "worsening"
    else:
        trend = "stable"

    return {
        "week_start": dt_to_iso(week_start),
        "week_end": dt_to_iso(week_end),
        "unit": unit or "all",
        "total_falls": total_falls,
        "unwitnessed_falls": unwitnessed,
        "avg_response_time_seconds": avg_response,
        "median_response_time_seconds": median_response,
        "repeat_fall_residents": repeat_fall_names,
        "compliance_score": compliance,
        "trend_vs_prior_week": trend,
    }


# ---------------------------------------------------------------------------
# Board report (12-month aggregate)
# ---------------------------------------------------------------------------


async def get_board_report_data(db: AsyncSession) -> dict:
    """Aggregate 12 months of data with per-unit breakdowns for board reporting."""
    now = datetime.now(timezone.utc)
    twelve_months_ago = now - timedelta(days=365)

    result = await db.execute(
        select(Event)
        .where(Event.detected_at >= twelve_months_ago)
        .order_by(Event.detected_at)
    )
    events = list(result.scalars().all())

    # Per-unit aggregation
    unit_data: dict[str, dict] = defaultdict(
        lambda: {
            "falls": 0,
            "response_times": [],
            "unwitnessed": 0,
            "total_events": 0,
        }
    )
    for e in events:
        u = e.unit or "unknown"
        unit_data[u]["total_events"] += 1
        if e.event_type == "fall":
            unit_data[u]["falls"] += 1
            if e.confidence in ("medium", "low"):
                unit_data[u]["unwitnessed"] += 1
        if e.acknowledged_at and e.detected_at:
            unit_data[u]["response_times"].append(
                seconds_between(e.detected_at, e.acknowledged_at)
            )

    unit_summaries = []
    for unit_name, data in unit_data.items():
        rt = data["response_times"]
        avg_rt = round(sum(rt) / len(rt), 1) if rt else 0.0
        unwitnessed_rate = (
            round(data["unwitnessed"] / data["falls"], 2) if data["falls"] else 0.0
        )
        acked_in_time = sum(1 for t in rt if t <= 180)
        compliance = int((acked_in_time / len(rt)) * 100) if rt else 100
        unit_summaries.append(
            {
                "unit": unit_name,
                "falls": data["falls"],
                "avg_response_time": avg_rt,
                "unwitnessed_rate": unwitnessed_rate,
                "compliance_score": compliance,
            }
        )

    # Liability indicators
    all_response_times = [
        seconds_between(e.detected_at, e.acknowledged_at)
        for e in events
        if e.acknowledged_at and e.detected_at
    ]
    slow_responses = sum(1 for t in all_response_times if t > 180)
    unack_alerts = sum(1 for e in events if e.status in ("active", "escalated"))
    repeat_falls = sum(1 for e in events if e.is_repeat_fall)

    # Monthly trends
    monthly: dict[str, dict] = defaultdict(
        lambda: {"falls": 0, "response_times": []}
    )
    for e in events:
        if e.detected_at:
            month_key = e.detected_at.strftime("%Y-%m")
            if e.event_type == "fall":
                monthly[month_key]["falls"] += 1
            if e.acknowledged_at and e.detected_at:
                monthly[month_key]["response_times"].append(
                    seconds_between(e.detected_at, e.acknowledged_at)
                )

    trends_monthly = []
    for month_key in sorted(monthly.keys()):
        data = monthly[month_key]
        rt = data["response_times"]
        trends_monthly.append(
            {
                "month": month_key,
                "falls": data["falls"],
                "avg_response_time": round(sum(rt) / len(rt), 1) if rt else 0.0,
            }
        )

    return {
        "period": f"{twelve_months_ago.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
        "facility_name": "ElderOS Facility",
        "unit_summaries": unit_summaries,
        "liability_indicators": {
            "slow_responses": slow_responses,
            "unacknowledged_alerts": unack_alerts,
            "repeat_falls": repeat_falls,
        },
        "trends_monthly": trends_monthly,
    }
