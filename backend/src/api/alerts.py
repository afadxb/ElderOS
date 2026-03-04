from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.alert import AcknowledgeRequest, AlertEventResponse, ResolveRequest
from src.services import alert_service, audit_service

router = APIRouter()


@router.get("/active", response_model=list[AlertEventResponse])
async def get_active(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ALERTS_VIEW)),
):
    """Get all active and escalated alerts."""
    alerts = await alert_service.get_active_alerts(db)
    return [AlertEventResponse.model_validate(a) for a in alerts]


@router.get("/recent", response_model=list[AlertEventResponse])
async def get_recent(
    minutes: int = 60,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ALERTS_VIEW)),
):
    """Get events detected within the last N minutes."""
    events = await alert_service.get_recent_events(db, minutes)
    return [AlertEventResponse.model_validate(e) for e in events]


@router.get("/", response_model=list[AlertEventResponse])
async def get_events(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ALERTS_VIEW)),
):
    """Get the most recent events up to a limit."""
    events = await alert_service.get_all_events(db, limit)
    return [AlertEventResponse.model_validate(e) for e in events]


@router.get("/room/{room_id}", response_model=list[AlertEventResponse])
async def get_events_by_room(
    room_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ALERTS_VIEW)),
):
    """Get events for a specific room."""
    events = await alert_service.get_events_by_room(db, room_id, limit)
    return [AlertEventResponse.model_validate(e) for e in events]


@router.post("/{event_id}/acknowledge", response_model=AlertEventResponse)
async def acknowledge(
    event_id: str,
    body: AcknowledgeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ALERTS_ACKNOWLEDGE)),
):
    """Acknowledge an active alert."""
    event = await alert_service.acknowledge_alert(db, event_id, body.user_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not active")

    # Audit log
    await audit_service.log_action(
        db, user.id, "acknowledge", "event", event_id,
    )
    await db.commit()

    # Broadcast via WebSocket
    ws_manager = request.app.state.ws_manager
    alert_data = AlertEventResponse.model_validate(event).model_dump(by_alias=True)
    await ws_manager.broadcast_alert(alert_data)
    await ws_manager.broadcast_data_change([["rooms"]])

    return AlertEventResponse.model_validate(event)


@router.post("/{event_id}/resolve", response_model=AlertEventResponse)
async def resolve(
    event_id: str,
    body: ResolveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ALERTS_RESOLVE)),
):
    """Resolve an active or acknowledged alert."""
    event = await alert_service.resolve_alert(db, event_id, body.user_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not resolvable")

    # Audit log
    await audit_service.log_action(
        db, user.id, "resolve", "event", event_id,
    )
    await db.commit()

    # Broadcast via WebSocket
    ws_manager = request.app.state.ws_manager
    alert_data = AlertEventResponse.model_validate(event).model_dump(by_alias=True)
    await ws_manager.broadcast_alert(alert_data)
    await ws_manager.broadcast_data_change([["rooms"]])

    return AlertEventResponse.model_validate(event)
