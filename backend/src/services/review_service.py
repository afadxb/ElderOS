from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event


async def get_review_queue(db: AsyncSession) -> list[Event]:
    """Get events that need human review: medium confidence and still active."""
    result = await db.execute(
        select(Event)
        .where(Event.confidence == "medium", Event.status == "active")
        .order_by(desc(Event.detected_at))
    )
    return list(result.scalars().all())


async def triage_event(
    db: AsyncSession, event_id: str, action: str
) -> Event | None:
    """Triage a review-queue event.

    action='confirm' keeps the event active (confirmed by human).
    action='dismiss' sets the event to dismissed.

    Returns the updated event or None if not found.
    """
    event = await db.get(Event, event_id)
    if not event:
        return None

    if action == "dismiss":
        event.status = "dismissed"
    # 'confirm' keeps it active — no status change needed, but we mark
    # confidence as validated by bumping it to 'high' so it exits the queue.
    elif action == "confirm":
        event.confidence = "high"

    await db.commit()
    await db.refresh(event)
    return event
