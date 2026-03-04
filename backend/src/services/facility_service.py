import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.resident import Resident
from src.models.room import Room
from src.models.sensor import Sensor
from src.models.unit import Unit


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------


async def get_units_with_counts(db: AsyncSession) -> list[dict]:
    """Get all units with their room counts."""
    room_count_sub = (
        select(Room.unit_id, func.count(Room.id).label("room_count"))
        .group_by(Room.unit_id)
        .subquery()
    )
    query = select(
        Unit.id,
        Unit.name,
        Unit.floor,
        func.coalesce(room_count_sub.c.room_count, 0).label("room_count"),
    ).outerjoin(room_count_sub, Unit.id == room_count_sub.c.unit_id)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": row.id,
            "name": row.name,
            "floor": row.floor,
            "room_count": row.room_count,
        }
        for row in rows
    ]


async def add_unit(db: AsyncSession, name: str, floor: int) -> Unit:
    """Create a new unit."""
    unit = Unit(
        id=str(uuid.uuid4()),
        name=name,
        floor=floor,
        created_at=datetime.now(timezone.utc),
    )
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    return unit


async def update_unit(
    db: AsyncSession, unit_id: str, name: str, floor: int
) -> Unit | None:
    """Update unit and cascade name/floor changes to rooms and residents."""
    unit = await db.get(Unit, unit_id)
    if not unit:
        return None

    old_name = unit.name
    unit.name = name
    unit.floor = floor

    # Cascade unit_name to rooms
    rooms_result = await db.execute(
        select(Room).where(Room.unit_id == unit_id)
    )
    rooms = list(rooms_result.scalars().all())
    for room in rooms:
        room.unit_name = name
        room.floor = floor

    # Cascade unit name to residents
    if old_name != name:
        residents_result = await db.execute(
            select(Resident).where(Resident.unit == old_name)
        )
        residents = list(residents_result.scalars().all())
        for resident in residents:
            resident.unit = name

    await db.commit()
    await db.refresh(unit)
    return unit


async def remove_unit(db: AsyncSession, unit_id: str) -> bool:
    """Delete a unit and cascade to rooms, residents, and sensors."""
    unit = await db.get(Unit, unit_id)
    if not unit:
        return False

    # Find rooms belonging to this unit
    rooms_result = await db.execute(
        select(Room.id).where(Room.unit_id == unit_id)
    )
    room_ids = [row[0] for row in rooms_result.all()]

    if room_ids:
        # Delete sensors in those rooms
        await db.execute(
            delete(Sensor).where(Sensor.room_id.in_(room_ids))
        )
        # Delete residents in those rooms
        await db.execute(
            delete(Resident).where(Resident.room_id.in_(room_ids))
        )
        # Delete rooms
        await db.execute(
            delete(Room).where(Room.id.in_(room_ids))
        )

    # Delete the unit
    await db.delete(unit)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------------------


async def get_rooms_by_unit(
    db: AsyncSession, unit: str | None = None
) -> list[Room]:
    """Get rooms, optionally filtered by unit name."""
    query = select(Room)
    if unit:
        query = query.where(Room.unit_name == unit)
    query = query.order_by(Room.number)
    result = await db.execute(query)
    return list(result.scalars().all())


async def add_room(
    db: AsyncSession,
    unit_name: str,
    floor: int,
    room_number: str,
    room_type: str,
    sensor_type: str,
) -> Room:
    """Create a room and auto-create sensors based on sensor_type.

    ai-vision  -> 1 sensor (ai-vision)
    ai-sensor  -> 1 sensor (ai-sensor)
    hybrid     -> 2 sensors (ai-vision + ai-sensor)
    """
    # Look up unit to get unit_id
    unit_result = await db.execute(
        select(Unit).where(Unit.name == unit_name)
    )
    unit = unit_result.scalars().first()

    now = datetime.now(timezone.utc)
    room_id = str(uuid.uuid4())
    room = Room(
        id=room_id,
        number=room_number,
        unit_id=unit.id if unit else None,
        unit_name=unit_name,
        floor=floor,
        room_type=room_type,
        sensor_type=sensor_type,
        status="clear",
        status_color="green",
        has_exclusion_zone=False,
        created_at=now,
    )
    db.add(room)

    # Auto-create sensors
    sensor_types_to_create: list[str] = []
    if sensor_type == "ai-vision":
        sensor_types_to_create = ["ai-vision"]
    elif sensor_type == "ai-sensor":
        sensor_types_to_create = ["ai-sensor"]
    elif sensor_type == "hybrid":
        sensor_types_to_create = ["ai-vision", "ai-sensor"]

    for s_type in sensor_types_to_create:
        sensor = Sensor(
            id=str(uuid.uuid4()),
            room_id=room_id,
            room_number=room_number,
            type=s_type,
            status="online",
            last_heartbeat=now,
            inference_latency_ms=0,
            baseline_latency_ms=80,
            uptime=100.0,
            firmware_version="v1.0.0",
        )
        db.add(sensor)

    await db.commit()
    await db.refresh(room)
    return room


async def update_room(
    db: AsyncSession, room_id: str, updates: dict
) -> Room | None:
    """Partial update of a room. Only applies non-None fields from updates dict."""
    room = await db.get(Room, room_id)
    if not room:
        return None

    allowed_fields = {
        "number", "room_type", "sensor_type", "unit_name",
        "floor", "status", "status_color", "has_exclusion_zone",
    }
    for key, value in updates.items():
        if key in allowed_fields and value is not None:
            setattr(room, key, value)

    await db.commit()
    await db.refresh(room)
    return room


async def remove_room(db: AsyncSession, room_id: str) -> bool:
    """Delete a room and its associated residents and sensors."""
    room = await db.get(Room, room_id)
    if not room:
        return False

    await db.execute(delete(Sensor).where(Sensor.room_id == room_id))
    await db.execute(delete(Resident).where(Resident.room_id == room_id))
    await db.delete(room)
    await db.commit()
    return True
