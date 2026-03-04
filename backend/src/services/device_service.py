import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sensor import Sensor
from src.utils.time_utils import dt_to_iso


def _parse_json(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _sensor_to_dict(s: Sensor) -> dict:
    return {
        "id": s.id,
        "room_id": s.room_id,
        "room_number": s.room_number,
        "type": s.type,
        "name": s.name,
        "status": s.status,
        "enabled": s.enabled,
        "edge_device_id": s.edge_device_id,
        "last_heartbeat": dt_to_iso(s.last_heartbeat),
        "inference_latency_ms": s.inference_latency_ms,
        "baseline_latency_ms": s.baseline_latency_ms,
        "uptime": s.uptime,
        "firmware_version": s.firmware_version,
        "connection_config": _parse_json(s.connection_config),
        "detection_config": _parse_json(s.detection_config),
    }


async def get_devices(
    db: AsyncSession,
    room_id: str | None = None,
    device_type: str | None = None,
) -> list[dict]:
    query = select(Sensor)
    if room_id:
        query = query.where(Sensor.room_id == room_id)
    if device_type:
        query = query.where(Sensor.type == device_type)
    query = query.order_by(Sensor.room_number, Sensor.type)
    result = await db.execute(query)
    return [_sensor_to_dict(s) for s in result.scalars().all()]


async def get_device(db: AsyncSession, device_id: str) -> dict | None:
    sensor = await db.get(Sensor, device_id)
    if not sensor:
        return None
    return _sensor_to_dict(sensor)


async def create_device(db: AsyncSession, data: dict) -> dict:
    sensor = Sensor(
        id=str(uuid.uuid4()),
        room_id=data["room_id"],
        room_number=data.get("room_number"),
        type=data.get("type"),
        name=data.get("name"),
        status="offline",
        enabled=data.get("enabled", True),
        edge_device_id=data.get("edge_device_id"),
        connection_config=json.dumps(data["connection_config"]) if data.get("connection_config") else None,
        detection_config=json.dumps(data["detection_config"]) if data.get("detection_config") else None,
    )
    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return _sensor_to_dict(sensor)


async def update_device(db: AsyncSession, device_id: str, updates: dict) -> dict | None:
    sensor = await db.get(Sensor, device_id)
    if not sensor:
        return None

    for field in ("room_id", "room_number", "type", "name", "edge_device_id", "enabled"):
        if field in updates and updates[field] is not None:
            setattr(sensor, field, updates[field])

    if "connection_config" in updates:
        sensor.connection_config = json.dumps(updates["connection_config"]) if updates["connection_config"] else None
    if "detection_config" in updates:
        sensor.detection_config = json.dumps(updates["detection_config"]) if updates["detection_config"] else None

    await db.commit()
    await db.refresh(sensor)
    return _sensor_to_dict(sensor)


async def delete_device(db: AsyncSession, device_id: str) -> bool:
    sensor = await db.get(Sensor, device_id)
    if not sensor:
        return False
    await db.delete(sensor)
    await db.commit()
    return True


async def get_edge_config(db: AsyncSession, edge_device_id: str) -> list[dict]:
    result = await db.execute(
        select(Sensor).where(
            Sensor.edge_device_id == edge_device_id,
            Sensor.enabled.is_(True),
        )
    )
    sensors = result.scalars().all()
    return [
        {
            "sensor_id": s.id,
            "room_id": s.room_id,
            "room_number": s.room_number,
            "type": s.type,
            "name": s.name,
            "connection_config": _parse_json(s.connection_config),
            "detection_config": _parse_json(s.detection_config),
        }
        for s in sensors
    ]
