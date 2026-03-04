from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.room import BedZoneResponse, BedZoneUpdate, RoomResponse
from src.services import room_service

router = APIRouter()


@router.get("/", response_model=list[RoomResponse])
async def get_rooms(
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """Get all rooms with nested residents and sensors. Optionally filter by unit."""
    rooms = await room_service.get_rooms(db, unit)
    return [RoomResponse(**r) for r in rooms]


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """Get a single room by ID."""
    room = await room_service.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomResponse(**room)


# --- Bed-Zone Management ---------------------------------------------------


@router.get("/zones/all", response_model=list[BedZoneResponse])
async def get_all_zones(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """Get bed-zone vertices for all rooms (used by edge devices to sync zones)."""
    return await room_service.get_all_zones(db)


@router.get("/{room_id}/zone", response_model=BedZoneResponse)
async def get_zone(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """Get bed-zone polygon for a room."""
    zone = await room_service.get_zone(db, room_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Room not found")
    return zone


@router.put("/{room_id}/zone", response_model=BedZoneResponse)
async def update_zone(
    room_id: str,
    body: BedZoneUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """Set or update bed-zone polygon for a room."""
    if len(body.vertices) < 3:
        raise HTTPException(status_code=422, detail="Zone requires at least 3 vertices")
    for v in body.vertices:
        if len(v) != 2 or not all(0.0 <= c <= 1.0 for c in v):
            raise HTTPException(
                status_code=422,
                detail="Each vertex must be [x, y] with values between 0.0 and 1.0",
            )
    zone = await room_service.update_zone(db, room_id, body.label, body.vertices)
    if not zone:
        raise HTTPException(status_code=404, detail="Room not found")
    return zone


@router.delete("/{room_id}/zone")
async def delete_zone(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.ROOMS_VIEW)),
):
    """Remove bed-zone polygon from a room."""
    deleted = await room_service.delete_zone(db, room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"detail": "Zone deleted"}
