from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.facility import (
    CreateRoomRequest,
    CreateUnitRequest,
    UpdateRoomRequest,
    UpdateUnitRequest,
    UnitResponse,
)
from src.schemas.room import RoomResponse
from src.services import facility_service, room_service, audit_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------


@router.get("/units", response_model=list[UnitResponse])
async def get_units(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """List all units with room counts."""
    units = await facility_service.get_units(db)
    return [UnitResponse.model_validate(u) for u in units]


@router.post("/units", response_model=UnitResponse, status_code=201)
async def create_unit(
    body: CreateUnitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Create a new facility unit."""
    unit = await facility_service.create_unit(db, body.name, body.floor)
    await audit_service.log_action(
        db, user.id, "create", "unit", unit.id,
        details={"name": body.name, "floor": body.floor},
    )
    await db.commit()
    return UnitResponse.model_validate(unit)


@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: str,
    body: UpdateUnitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update an existing unit."""
    unit = await facility_service.update_unit(db, unit_id, body.name, body.floor)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    await audit_service.log_action(
        db, user.id, "update", "unit", unit_id,
        details={"name": body.name, "floor": body.floor},
    )
    await db.commit()
    return UnitResponse.model_validate(unit)


@router.delete("/units/{unit_id}", status_code=204)
async def delete_unit(
    unit_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Delete a unit and cascade to its rooms."""
    deleted = await facility_service.delete_unit(db, unit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Unit not found")
    await audit_service.log_action(db, user.id, "delete", "unit", unit_id)
    await db.commit()

    # Broadcast facility data change
    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["rooms"], ["units"]])


# ---------------------------------------------------------------------------
# Rooms (facility management)
# ---------------------------------------------------------------------------


@router.get("/rooms", response_model=list[RoomResponse])
async def get_facility_rooms(
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """List all rooms. Optionally filter by unit."""
    rooms = await room_service.get_rooms(db, unit)
    return [RoomResponse(**r) for r in rooms]


@router.post("/rooms", response_model=RoomResponse, status_code=201)
async def create_room(
    body: CreateRoomRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Create a new room in a unit."""
    room_dict = await facility_service.create_room(
        db,
        unit_name=body.unit_name,
        floor=body.floor,
        room_number=body.room_number,
        room_type=body.room_type,
        sensor_type=body.sensor_type,
    )
    await audit_service.log_action(
        db, user.id, "create", "room", room_dict["id"],
        details={"room_number": body.room_number, "unit": body.unit_name},
    )
    await db.commit()

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["rooms"]])
    return RoomResponse(**room_dict)


@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    body: UpdateRoomRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update a room's properties."""
    room_dict = await facility_service.update_room(
        db,
        room_id,
        number=body.number,
        room_type=body.room_type,
        sensor_type=body.sensor_type,
        unit=body.unit,
        floor=body.floor,
    )
    if not room_dict:
        raise HTTPException(status_code=404, detail="Room not found")
    await audit_service.log_action(
        db, user.id, "update", "room", room_id,
    )
    await db.commit()

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["rooms"]])
    return RoomResponse(**room_dict)


@router.delete("/rooms/{room_id}", status_code=204)
async def delete_room(
    room_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Delete a room and cascade to sensors/residents."""
    deleted = await facility_service.delete_room(db, room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    await audit_service.log_action(db, user.id, "delete", "room", room_id)
    await db.commit()

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["rooms"]])
