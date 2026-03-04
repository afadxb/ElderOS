import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event
from src.models.room import Room


async def get_active_alerts(db: AsyncSession) -> list[Event]:
    """Get all active and escalated alerts."""
    result = await db.execute(
        select(Event)
        .where(Event.status.in_(["active", "escalated"]))
        .order_by(desc(Event.detected_at))
    )
    return list(result.scalars().all())


async def get_recent_events(
    db: AsyncSession, minutes: int = 60
) -> list[Event]:
    """Get events detected within the last N minutes."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    result = await db.execute(
        select(Event)
        .where(Event.detected_at >= cutoff)
        .order_by(desc(Event.detected_at))
    )
    return list(result.scalars().all())


async def get_all_events(
    db: AsyncSession, limit: int = 50
) -> list[Event]:
    """Get the most recent events up to a limit."""
    result = await db.execute(
        select(Event).order_by(desc(Event.detected_at)).limit(limit)
    )
    return list(result.scalars().all())


async def get_events_by_room(
    db: AsyncSession, room_id: str, limit: int = 20
) -> list[Event]:
    """Get events for a specific room."""
    result = await db.execute(
        select(Event)
        .where(Event.room_id == room_id)
        .order_by(desc(Event.detected_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def acknowledge_alert(
    db: AsyncSession, event_id: str, user_id: str
) -> Event | None:
    """Acknowledge an active alert. Returns updated event or None."""
    event = await db.get(Event, event_id)
    if not event or event.status != "active":
        return None

    event.status = "acknowledged"
    event.acknowledged_at = datetime.now(timezone.utc)
    event.acknowledged_by = user_id

    # Update room status to attention / yellow
    room = await db.get(Room, event.room_id)
    if room and room.status == "active-alert":
        room.status = "attention"
        room.status_color = "yellow"

    await db.commit()
    await db.refresh(event)
    return event


async def resolve_alert(
    db: AsyncSession, event_id: str, user_id: str
) -> Event | None:
    """Resolve an active or acknowledged alert. Returns updated event or None."""
    event = await db.get(Event, event_id)
    if not event or event.status not in ("active", "acknowledged", "escalated"):
        return None

    now = datetime.now(timezone.utc)
    # If resolving directly from active, also set ack fields
    if event.acknowledged_at is None:
        event.acknowledged_at = now
        event.acknowledged_by = user_id

    event.status = "resolved"
    event.resolved_at = now
    event.resolved_by = user_id

    # Check if room has other active alerts before clearing
    room = await db.get(Room, event.room_id)
    if room:
        count = await db.scalar(
            select(func.count()).where(
                Event.room_id == room.id,
                Event.status.in_(["active", "escalated"]),
                Event.id != event_id,
            )
        )
        if count == 0:
            room.status = "clear"
            room.status_color = "green"

    await db.commit()
    await db.refresh(event)
    return event


async def create_event(db: AsyncSession, **kwargs) -> Event:
    """Create a new alert event (typically from an edge device)."""
    event = Event(id=str(uuid.uuid4()), **kwargs)
    db.add(event)

    # Update room status to active-alert
    room = await db.get(Room, event.room_id)
    if room:
        room.status = "active-alert"
        room.status_color = "red"
        room.last_event_at = event.detected_at

    await db.commit()
    await db.refresh(event)
    return event
