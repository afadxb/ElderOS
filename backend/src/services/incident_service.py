import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.event import Event
from src.models.incident import Incident
from src.utils.pagination import paginate
from src.utils.time_utils import seconds_between


async def get_incidents(db: AsyncSession, filters: dict) -> dict:
    """Get paginated incidents with optional filters.

    Supported filters: unit, event_type, status, page, page_size.
    Returns paginate() dict: {data, total, page, page_size, total_pages}.
    """
    query = select(Incident).order_by(desc(Incident.detected_at))

    unit = filters.get("unit")
    if unit:
        query = query.where(Incident.unit == unit)

    event_type = filters.get("event_type")
    if event_type:
        query = query.where(Incident.event_type == event_type)

    status = filters.get("status")
    if status:
        query = query.where(Incident.status == status)

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)

    return await paginate(db, query, page=page, page_size=page_size)


async def get_incident_by_id(
    db: AsyncSession, incident_id: str
) -> Incident | None:
    """Get a single incident with eagerly loaded escalation steps."""
    query = (
        select(Incident)
        .options(selectinload(Incident.escalation_steps))
        .where(Incident.id == incident_id)
    )
    result = await db.execute(query)
    return result.scalars().unique().one_or_none()


async def get_incidents_by_resident(
    db: AsyncSession, resident_id: str, limit: int = 10
) -> list[Incident]:
    """Get recent incidents for a specific resident."""
    result = await db.execute(
        select(Incident)
        .where(Incident.resident_id == resident_id)
        .order_by(desc(Incident.detected_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_incident_from_event(
    db: AsyncSession, event: Event
) -> Incident:
    """Create an Incident record from a resolved event.

    Computes response time metrics from the event timestamps.
    """
    now = datetime.now(timezone.utc)

    ack_seconds = None
    if event.acknowledged_at and event.detected_at:
        ack_seconds = seconds_between(event.detected_at, event.acknowledged_at)

    resolve_seconds = None
    if event.resolved_at and event.detected_at:
        resolve_seconds = seconds_between(event.detected_at, event.resolved_at)

    incident = Incident(
        id=str(uuid.uuid4()),
        event_id=event.id,
        room_number=event.room_number,
        resident_name=event.resident_name,
        resident_id=event.resident_id,
        event_type=event.event_type,
        confidence=event.confidence,
        confidence_score=event.confidence_score,
        status=event.status,
        ntp_timestamp=event.detected_at.isoformat() if event.detected_at else None,
        detected_at=event.detected_at,
        acknowledged_at=event.acknowledged_at,
        resolved_at=event.resolved_at,
        ack_response_seconds=ack_seconds,
        resolve_response_seconds=resolve_seconds,
        acknowledged_by=event.acknowledged_by,
        resolved_by=event.resolved_by,
        pre_event_summary=event.pre_event_summary,
        post_event_state=event.post_event_state,
        is_repeat_fall=event.is_repeat_fall,
        notes="",
        unit=event.unit,
        sensor_source=event.sensor_source,
        bed_zone=event.bed_zone,
        created_at=now,
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident
