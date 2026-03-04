from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.resident import Resident
from src.models.user import User
from src.schemas.resident import ResidentResponse

router = APIRouter()


@router.get("/", response_model=list[ResidentResponse])
async def get_residents(
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.RESIDENTS_VIEW)),
):
    """Get all residents. Optionally filter by unit."""
    query = select(Resident).order_by(Resident.name)
    if unit:
        query = query.where(Resident.unit == unit)
    result = await db.execute(query)
    residents = list(result.scalars().all())
    return [ResidentResponse.model_validate(r) for r in residents]


@router.get("/high-risk", response_model=list[ResidentResponse])
async def get_high_risk_residents(
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.RESIDENTS_VIEW)),
):
    """Get residents with a risk score of 70 or higher."""
    query = (
        select(Resident)
        .where(Resident.risk_score >= 70)
        .order_by(desc(Resident.risk_score))
    )
    if unit:
        query = query.where(Resident.unit == unit)
    result = await db.execute(query)
    residents = list(result.scalars().all())
    return [ResidentResponse.model_validate(r) for r in residents]


@router.get("/{resident_id}", response_model=ResidentResponse)
async def get_resident(
    resident_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.RESIDENTS_VIEW)),
):
    """Get a single resident by ID."""
    resident = await db.get(Resident, resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return ResidentResponse.model_validate(resident)
