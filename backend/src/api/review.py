from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.event import Event
from src.models.user import User
from src.schemas.alert import AlertEventResponse
from src.schemas.review import TriageRequest
from src.services import audit_service

router = APIRouter()


@router.get("/queue", response_model=list[AlertEventResponse])
async def get_review_queue(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REVIEW_VIEW)),
):
    """Get events that require manual review (medium confidence, active status)."""
    query = (
        select(Event)
        .where(Event.confidence == "medium", Event.status == "active")
        .order_by(Event.detected_at.desc())
    )
    result = await db.execute(query)
    events = list(result.scalars().all())
    return [AlertEventResponse.model_validate(e) for e in events]


@router.post("/{event_id}/triage", response_model=AlertEventResponse)
async def triage_event(
    event_id: str,
    body: TriageRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REVIEW_TRIAGE)),
):
    """Triage a review queue event: confirm as real alert or dismiss as false positive."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != "active":
        raise HTTPException(status_code=400, detail="Event is not in active status")

    if body.action == "confirm":
        event.confidence = "high"
    elif body.action == "dismiss":
        event.status = "dismissed"

    await db.commit()
    await db.refresh(event)

    # Audit log
    await audit_service.log_action(
        db, user.id, f"triage_{body.action}", "event", event_id,
    )
    await db.commit()

    # Broadcast via WebSocket
    ws_manager = request.app.state.ws_manager
    alert_data = AlertEventResponse.model_validate(event).model_dump(by_alias=True)
    await ws_manager.broadcast_alert(alert_data)
    await ws_manager.broadcast_data_change([["rooms"], ["alerts"]])

    return AlertEventResponse.model_validate(event)
