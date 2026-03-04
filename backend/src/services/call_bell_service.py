from collections import Counter, defaultdict
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.call_bell import CallBellEvent
from src.utils.pagination import paginate
from src.utils.time_utils import get_shift_name, seconds_between


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def _apply_common_filters(query, filters: dict):
    """Apply common filter predicates to a CallBellEvent query."""
    if filters.get("unit"):
        query = query.where(CallBellEvent.unit == filters["unit"])
    if filters.get("floor"):
        query = query.where(CallBellEvent.floor == filters["floor"])
    if filters.get("shift"):
        query = query.where(CallBellEvent.shift == filters["shift"])
    if filters.get("priority"):
        query = query.where(CallBellEvent.priority == filters["priority"])
    if filters.get("status"):
        query = query.where(CallBellEvent.status == filters["status"])
    if filters.get("date_from"):
        query = query.where(CallBellEvent.pressed_at >= filters["date_from"])
    if filters.get("date_to"):
        query = query.where(CallBellEvent.pressed_at <= filters["date_to"])
    return query


async def _load_filtered_events(
    db: AsyncSession, filters: dict
) -> list[CallBellEvent]:
    """Load call bell events matching filters (unpaginated, for metrics)."""
    query = select(CallBellEvent).order_by(desc(CallBellEvent.pressed_at))
    query = _apply_common_filters(query, filters)
    result = await db.execute(query)
    return list(result.scalars().all())


def _median(values: list[int | float]) -> float:
    """Compute median of a list of numbers."""
    if not values:
        return 0.0
    s = sorted(values)
    mid = len(s) // 2
    if len(s) % 2 == 0:
        return round((s[mid - 1] + s[mid]) / 2, 1)
    return float(s[mid])


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


async def get_call_bell_events(db: AsyncSession, filters: dict) -> dict:
    """Get paginated call bell events with filters.

    Supported filters: unit, floor, shift, priority, status,
    date_from, date_to, page, page_size.
    """
    query = select(CallBellEvent).order_by(desc(CallBellEvent.pressed_at))
    query = _apply_common_filters(query, filters)

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    return await paginate(db, query, page=page, page_size=page_size)


async def get_active_call_bells(db: AsyncSession) -> list[CallBellEvent]:
    """Get call bells that are still active or responded (not yet closed)."""
    result = await db.execute(
        select(CallBellEvent)
        .where(CallBellEvent.status.in_(["active", "responded"]))
        .order_by(desc(CallBellEvent.pressed_at))
    )
    return list(result.scalars().all())


async def respond_to_call_bell(
    db: AsyncSession, event_id: str, user_id: str, user_name: str
) -> CallBellEvent | None:
    """Mark a call bell as responded and compute response time."""
    event = await db.get(CallBellEvent, event_id)
    if not event or event.status != "active":
        return None

    now = datetime.now(timezone.utc)
    event.status = "responded"
    event.responded_at = now
    event.responded_by = user_id
    event.responded_by_name = user_name

    if event.pressed_at:
        event.response_time_seconds = seconds_between(event.pressed_at, now)

    await db.commit()
    await db.refresh(event)
    return event


async def close_call_bell(
    db: AsyncSession, event_id: str
) -> CallBellEvent | None:
    """Mark a call bell as closed."""
    event = await db.get(CallBellEvent, event_id)
    if not event or event.status not in ("active", "responded"):
        return None

    event.status = "closed"
    event.closed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(event)
    return event


# ---------------------------------------------------------------------------
# Staff metrics
# ---------------------------------------------------------------------------


async def get_staff_metrics(db: AsyncSession, filters: dict) -> list[dict]:
    """Compute per-staff response metrics.

    Groups by responded_by. Computes avg, min, max, median response times
    and counts calls under 60s, under 120s, over 180s.
    """
    events = await _load_filtered_events(db, filters)

    # Only include events that have a responder and a response time
    staff_events: dict[str, list[CallBellEvent]] = defaultdict(list)
    for e in events:
        if e.responded_by and e.response_time_seconds is not None:
            staff_events[e.responded_by].append(e)

    metrics: list[dict] = []
    for staff_id, evts in staff_events.items():
        times = [e.response_time_seconds for e in evts if e.response_time_seconds is not None]
        if not times:
            continue

        # Use the name from the first event that has one
        staff_name = next(
            (e.responded_by_name for e in evts if e.responded_by_name), staff_id
        )

        metrics.append(
            {
                "staff_id": staff_id,
                "staff_name": staff_name,
                "role": "staff",
                "total_calls": len(evts),
                "avg_response_seconds": round(sum(times) / len(times), 1),
                "median_response_seconds": _median(times),
                "min_response_seconds": float(min(times)),
                "max_response_seconds": float(max(times)),
                "calls_under_60s": sum(1 for t in times if t < 60),
                "calls_under_120s": sum(1 for t in times if t < 120),
                "calls_over_180s": sum(1 for t in times if t > 180),
            }
        )

    return metrics


# ---------------------------------------------------------------------------
# Floor metrics
# ---------------------------------------------------------------------------


async def get_floor_metrics(db: AsyncSession, filters: dict) -> list[dict]:
    """Compute per-floor/unit call bell metrics.

    Groups by (floor, unit). Computes calls by priority and origin, and
    finds the peak hour.
    """
    events = await _load_filtered_events(db, filters)

    floor_events: dict[tuple[int | None, str | None], list[CallBellEvent]] = defaultdict(list)
    for e in events:
        floor_events[(e.floor, e.unit)].append(e)

    metrics: list[dict] = []
    for (floor_val, unit_val), evts in floor_events.items():
        times = [
            e.response_time_seconds
            for e in evts
            if e.response_time_seconds is not None
        ]
        avg_response = round(sum(times) / len(times), 1) if times else 0.0

        priority_counts: dict[str, int] = dict(
            Counter(e.priority for e in evts if e.priority)
        )
        origin_counts: dict[str, int] = dict(
            Counter(e.origin for e in evts if e.origin)
        )

        # Peak hour
        hour_counts: dict[int, int] = Counter(
            e.pressed_at.hour for e in evts if e.pressed_at
        )
        peak_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 0

        metrics.append(
            {
                "floor": floor_val or 0,
                "unit": unit_val or "unknown",
                "total_calls": len(evts),
                "avg_response_seconds": avg_response,
                "calls_by_priority": priority_counts,
                "calls_by_origin": origin_counts,
                "peak_hour": peak_hour,
            }
        )

    return metrics


# ---------------------------------------------------------------------------
# Shift metrics
# ---------------------------------------------------------------------------


async def get_shift_metrics(db: AsyncSession, filters: dict) -> list[dict]:
    """Compute per-shift call bell metrics.

    Groups by (shift, date, unit).
    """
    events = await _load_filtered_events(db, filters)

    shift_events: dict[tuple[str, str, str], list[CallBellEvent]] = defaultdict(list)
    for e in events:
        shift = e.shift or (
            get_shift_name(e.pressed_at.hour) if e.pressed_at else "Unknown"
        )
        date_str = e.pressed_at.strftime("%Y-%m-%d") if e.pressed_at else "unknown"
        unit_val = e.unit or "unknown"
        shift_events[(shift, date_str, unit_val)].append(e)

    metrics: list[dict] = []
    for (shift, date_str, unit_val), evts in shift_events.items():
        times = [
            e.response_time_seconds
            for e in evts
            if e.response_time_seconds is not None
        ]
        avg_response = round(sum(times) / len(times), 1) if times else 0.0

        metrics.append(
            {
                "shift": shift,
                "date": date_str,
                "unit": unit_val,
                "total_calls": len(evts),
                "avg_response_seconds": avg_response,
                "responded_within_60s": sum(1 for t in times if t <= 60),
                "responded_within_120s": sum(1 for t in times if t <= 120),
                "slow_responses": sum(1 for t in times if t > 180),
            }
        )

    return metrics


# ---------------------------------------------------------------------------
# Daily summaries
# ---------------------------------------------------------------------------


async def get_daily_summaries(
    db: AsyncSession, unit: str | None = None
) -> list[dict]:
    """Compute daily call bell summaries grouped by date."""
    query = select(CallBellEvent).order_by(desc(CallBellEvent.pressed_at))
    if unit:
        query = query.where(CallBellEvent.unit == unit)

    result = await db.execute(query)
    events = list(result.scalars().all())

    daily: dict[str, list[CallBellEvent]] = defaultdict(list)
    for e in events:
        if e.pressed_at:
            date_str = e.pressed_at.strftime("%Y-%m-%d")
            daily[date_str].append(e)

    summaries: list[dict] = []
    for date_str in sorted(daily.keys(), reverse=True):
        evts = daily[date_str]
        times = [
            e.response_time_seconds
            for e in evts
            if e.response_time_seconds is not None
        ]
        avg_response = round(sum(times) / len(times), 1) if times else 0.0

        summaries.append(
            {
                "date": date_str,
                "total_calls": len(evts),
                "avg_response_seconds": avg_response,
            }
        )

    return summaries
