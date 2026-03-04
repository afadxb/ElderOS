from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.call_bell import (
    CallBellDailySummaryResponse,
    CallBellEventResponse,
    CallBellFloorMetricsResponse,
    CallBellRespondRequest,
    CallBellShiftMetricsResponse,
    CallBellStaffMetricsResponse,
)
from src.schemas.common import PaginatedResponse
from src.services import call_bell_service, audit_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CallBellEventResponse])
async def get_call_bell_events(
    unit: str | None = None,
    floor: int | None = None,
    shift: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_VIEW)),
):
    """Get paginated call bell events with multiple filters."""
    result = await call_bell_service.get_events(
        db,
        unit=unit,
        floor=floor,
        shift=shift,
        priority=priority,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    result["data"] = [
        CallBellEventResponse.model_validate(e) for e in result["data"]
    ]
    return result


@router.get("/active", response_model=list[CallBellEventResponse])
async def get_active_call_bells(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_VIEW)),
):
    """Get active and responded (not yet closed) call bell events."""
    events = await call_bell_service.get_active_events(db)
    return [CallBellEventResponse.model_validate(e) for e in events]


@router.post("/{event_id}/respond", response_model=CallBellEventResponse)
async def respond_to_call_bell(
    event_id: str,
    body: CallBellRespondRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_RESPOND)),
):
    """Mark a call bell event as responded."""
    event = await call_bell_service.respond(
        db, event_id, body.user_id, body.user_name,
    )
    if not event:
        raise HTTPException(status_code=404, detail="Call bell event not found or not active")

    await audit_service.log_action(
        db, user.id, "respond", "call_bell", event_id,
    )
    await db.commit()

    # Broadcast via WebSocket
    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["call_bells"]])

    return CallBellEventResponse.model_validate(event)


@router.post("/{event_id}/close", response_model=CallBellEventResponse)
async def close_call_bell(
    event_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_RESPOND)),
):
    """Close a responded call bell event."""
    event = await call_bell_service.close(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Call bell event not found or not responded")

    await audit_service.log_action(
        db, user.id, "close", "call_bell", event_id,
    )
    await db.commit()

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["call_bells"]])

    return CallBellEventResponse.model_validate(event)


# ---------------------------------------------------------------------------
# Analytics / Metrics
# ---------------------------------------------------------------------------


@router.get("/metrics/staff", response_model=list[CallBellStaffMetricsResponse])
async def get_staff_metrics(
    unit: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_ANALYTICS)),
):
    """Get call bell response metrics broken down by staff member."""
    metrics = await call_bell_service.get_staff_metrics(
        db, unit=unit, date_from=date_from, date_to=date_to,
    )
    return [CallBellStaffMetricsResponse.model_validate(m) for m in metrics]


@router.get("/metrics/floor", response_model=list[CallBellFloorMetricsResponse])
async def get_floor_metrics(
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_ANALYTICS)),
):
    """Get call bell metrics broken down by floor."""
    metrics = await call_bell_service.get_floor_metrics(
        db, date_from=date_from, date_to=date_to,
    )
    return [CallBellFloorMetricsResponse.model_validate(m) for m in metrics]


@router.get("/metrics/shift", response_model=list[CallBellShiftMetricsResponse])
async def get_shift_metrics(
    unit: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_ANALYTICS)),
):
    """Get call bell metrics broken down by shift."""
    metrics = await call_bell_service.get_shift_metrics(
        db, unit=unit, date_from=date_from, date_to=date_to,
    )
    return [CallBellShiftMetricsResponse.model_validate(m) for m in metrics]


@router.get("/metrics/daily", response_model=list[CallBellDailySummaryResponse])
async def get_daily_metrics(
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.CALLBELL_ANALYTICS)),
):
    """Get daily call bell summary metrics."""
    metrics = await call_bell_service.get_daily_metrics(db, unit=unit)
    return [CallBellDailySummaryResponse.model_validate(m) for m in metrics]
