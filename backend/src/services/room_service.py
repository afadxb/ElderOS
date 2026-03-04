import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.resident import Resident
from src.models.room import Room
from src.models.sensor import Sensor
from src.utils.time_utils import dt_to_iso


def _parse_zone_vertices(raw: str | None) -> list[list[float]] | None:
    """Parse JSON zone vertices from the DB column."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _build_room_dict(room: Room, residents: list, sensors: list) -> dict:
    """Construct a room response dict with nested residents and sensors."""
    return {
        "id": room.id,
        "number": room.number,
        "unit": room.unit_name,
        "floor": room.floor,
        "room_type": room.room_type,
        "sensor_type": room.sensor_type,
        "status": room.status,
        "status_color": room.status_color,
        "last_event_at": dt_to_iso(room.last_event_at),
        "has_exclusion_zone": room.has_exclusion_zone,
        "bed_zone_vertices": _parse_zone_vertices(room.bed_zone_vertices),
        "residents": [
            {
                "resident_id": r.id,
                "resident_name": r.name,
                "bed_zone": r.bed_zone,
            }
            for r in residents
        ],
        "sensors": [
            {
                "id": s.id,
                "type": s.type,
                "online": s.status == "online",
                "last_heartbeat": dt_to_iso(s.last_heartbeat),
                "health_score": int(s.uptime),
            }
            for s in sensors
        ],
    }


async def get_rooms(
    db: AsyncSession, unit: str | None = None
) -> list[dict]:
    """Get all rooms with nested residents and sensors. Optionally filter by unit."""
    query = select(Room).options(
        selectinload(Room.residents),
        selectinload(Room.sensors),
    )
    if unit:
        query = query.where(Room.unit_name == unit)
    query = query.order_by(Room.number)

    result = await db.execute(query)
    rooms = list(result.scalars().unique().all())

    return [
        _build_room_dict(room, room.residents, room.sensors)
        for room in rooms
    ]


async def get_room_by_id(db: AsyncSession, room_id: str) -> dict | None:
    """Get a single room with nested residents and sensors."""
    query = (
        select(Room)
        .options(
            selectinload(Room.residents),
            selectinload(Room.sensors),
        )
        .where(Room.id == room_id)
    )
    result = await db.execute(query)
    room = result.scalars().unique().one_or_none()
    if not room:
        return None
    return _build_room_dict(room, room.residents, room.sensors)


async def update_room_status(
    db: AsyncSession, room_id: str, status: str, color: str
) -> Room | None:
    """Directly update room status and color."""
    room = await db.get(Room, room_id)
    if not room:
        return None
    room.status = status
    room.status_color = color
    await db.commit()
    await db.refresh(room)
    return room


async def get_zone(db: AsyncSession, room_id: str) -> dict | None:
    """Get bed-zone vertices for a room."""
    room = await db.get(Room, room_id)
    if not room:
        return None
    vertices = _parse_zone_vertices(room.bed_zone_vertices)
    return {
        "room_id": room.id,
        "label": "bed",
        "vertices": vertices or [],
    }


async def update_zone(
    db: AsyncSession, room_id: str, label: str, vertices: list[list[float]]
) -> dict | None:
    """Set bed-zone vertices for a room."""
    room = await db.get(Room, room_id)
    if not room:
        return None
    room.bed_zone_vertices = json.dumps(vertices)
    await db.commit()
    await db.refresh(room)
    return {
        "room_id": room.id,
        "label": label,
        "vertices": vertices,
    }


async def delete_zone(db: AsyncSession, room_id: str) -> bool:
    """Remove bed-zone vertices for a room."""
    room = await db.get(Room, room_id)
    if not room:
        return False
    room.bed_zone_vertices = None
    await db.commit()
    return True


async def get_all_zones(db: AsyncSession) -> list[dict]:
    """Get bed-zone vertices for all rooms that have them configured."""
    result = await db.execute(
        select(Room).where(Room.bed_zone_vertices.isnot(None))
    )
    rooms = result.scalars().all()
    return [
        {
            "room_id": r.id,
            "label": "bed",
            "vertices": _parse_zone_vertices(r.bed_zone_vertices) or [],
        }
        for r in rooms
    ]
