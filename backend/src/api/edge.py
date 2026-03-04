import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, verify_edge_api_key
from src.models.call_bell import CallBellEvent
from src.models.room import Room
from src.models.sensor import Sensor
from src.models.system_metrics import SystemMetrics
from src.schemas.alert import AlertEventResponse
from src.schemas.edge import (
    EdgeCallBellPayload,
    EdgeEventPayload,
    EdgeHealthPayload,
    EdgeMetricsPayload,
)
from src.services import alert_service, device_service
from src.utils.time_utils import get_shift_name, now_utc

router = APIRouter()


@router.post("/events", status_code=201)
async def ingest_event(
    body: EdgeEventPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_edge_api_key),
):
    """Ingest an alert event from an edge device.

    Creates the event record, updates room status, broadcasts via WebSocket,
    and initiates the escalation timer.
    """
    event = await alert_service.create_event(
        db,
        room_id=body.room_id,
        room_number=body.room_number,
        resident_id=body.resident_id,
        resident_name=body.resident_name,
        event_type=body.event_type,
        severity=body.severity,
        confidence=body.confidence,
        confidence_score=body.confidence_score,
        status="active",
        sensor_source=body.sensor_source,
        bed_zone=body.bed_zone,
        pre_event_summary=body.pre_event_summary,
        post_event_state=body.post_event_state,
        is_repeat_fall=body.is_repeat_fall,
        detected_at=body.detected_at,
        escalation_level=0,
        unit=(await _resolve_room_unit(db, body.room_id)),
    )

    # Broadcast the new alert via WebSocket
    ws_manager = request.app.state.ws_manager
    alert_data = AlertEventResponse.model_validate(event).model_dump(by_alias=True)
    await ws_manager.broadcast_alert(alert_data)
    await ws_manager.broadcast_data_change([["rooms"], ["alerts"]])

    return {"id": event.id, "status": "created"}


@router.post("/callbell", status_code=201)
async def ingest_call_bell(
    body: EdgeCallBellPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_edge_api_key),
):
    """Ingest a call bell event from an edge device."""
    now = now_utc()
    pressed = datetime.fromisoformat(body.pressed_at) if isinstance(body.pressed_at, str) else body.pressed_at
    shift = get_shift_name(pressed.hour)

    cb_event = CallBellEvent(
        id=str(uuid.uuid4()),
        room_id=body.room_id,
        room_number=body.room_number,
        resident_id=body.resident_id,
        resident_name=body.resident_name,
        unit=body.unit,
        floor=body.floor,
        origin=body.origin,
        priority=body.priority,
        status="active",
        vendor=body.vendor,
        pressed_at=pressed,
        shift=shift,
    )
    db.add(cb_event)
    await db.commit()
    await db.refresh(cb_event)

    # Broadcast via WebSocket
    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["call_bells"]])

    return {"id": cb_event.id, "status": "created"}


@router.post("/health", status_code=200)
async def ingest_health(
    body: EdgeHealthPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_edge_api_key),
):
    """Ingest sensor health data from edge devices. Upserts sensor records."""
    for s in body.sensors:
        existing = await db.get(Sensor, s.sensor_id)
        if existing:
            existing.type = s.type
            existing.room_id = s.room_id
            existing.room_number = s.room_number
            existing.status = s.status
            existing.last_heartbeat = datetime.fromisoformat(s.last_heartbeat) if isinstance(s.last_heartbeat, str) else s.last_heartbeat
            existing.inference_latency_ms = s.inference_latency_ms
            existing.baseline_latency_ms = s.baseline_latency_ms
            existing.uptime = s.uptime
            existing.firmware_version = s.firmware_version
        else:
            sensor = Sensor(
                id=s.sensor_id,
                room_id=s.room_id,
                room_number=s.room_number,
                type=s.type,
                status=s.status,
                last_heartbeat=datetime.fromisoformat(s.last_heartbeat) if isinstance(s.last_heartbeat, str) else s.last_heartbeat,
                inference_latency_ms=s.inference_latency_ms,
                baseline_latency_ms=s.baseline_latency_ms,
                uptime=s.uptime,
                firmware_version=s.firmware_version,
            )
            db.add(sensor)

    await db.commit()

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_system_update()

    return {"status": "ok", "sensors_processed": len(body.sensors)}


@router.post("/metrics", status_code=200)
async def ingest_metrics(
    body: EdgeMetricsPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_edge_api_key),
):
    """Ingest system metrics from the edge device."""
    metrics = SystemMetrics(
        id=str(uuid.uuid4()),
        cpu_usage=body.cpu_usage,
        memory_usage=body.memory_usage,
        disk_usage_percent=body.disk_usage_percent,
        disk_used_gb=body.disk_used_gb,
        disk_total_gb=body.disk_total_gb,
        ntp_drift_ms=body.ntp_drift_ms,
        ntp_sync_status=body.ntp_sync_status,
        last_self_test_at=(
            datetime.fromisoformat(body.last_self_test_at)
            if body.last_self_test_at
            else None
        ),
        self_test_passed=body.self_test_passed,
        edge_device_uptime=body.edge_device_uptime,
        recorded_at=now_utc(),
    )
    db.add(metrics)
    await db.commit()

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_system_update()

    return {"status": "ok"}


@router.get("/config")
async def get_edge_config(
    edge_device_id: str,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_edge_api_key),
):
    """Return device configs for a specific edge device (used by edge config sync)."""
    devices = await device_service.get_edge_config(db, edge_device_id)
    return {"edge_device_id": edge_device_id, "devices": devices}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _resolve_room_unit(db: AsyncSession, room_id: str) -> str | None:
    """Look up the unit name for a room."""
    room = await db.get(Room, room_id)
    return room.unit_name if room else None
