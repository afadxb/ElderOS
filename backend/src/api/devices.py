from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.device import (
    CreateDeviceRequest,
    DeviceResponse,
    UpdateDeviceRequest,
)
from src.services import device_service

router = APIRouter()


@router.get("/", response_model=list[DeviceResponse])
async def get_devices(
    room_id: str | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_VIEW)),
):
    """List all devices. Optionally filter by room_id or type."""
    return await device_service.get_devices(db, room_id=room_id, device_type=type)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_VIEW)),
):
    """Get a single device by ID."""
    device = await device_service.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/", response_model=DeviceResponse, status_code=201)
async def create_device(
    body: CreateDeviceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_MANAGE)),
):
    """Create a new device."""
    return await device_service.create_device(db, body.model_dump())


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    body: UpdateDeviceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_MANAGE)),
):
    """Update an existing device."""
    device = await device_service.update_device(
        db, device_id, body.model_dump(exclude_unset=True)
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_MANAGE)),
):
    """Delete a device."""
    deleted = await device_service.delete_device(db, device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"detail": "Device deleted"}
