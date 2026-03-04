from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.resident import Resident


async def get_residents(
    db: AsyncSession, unit: str | None = None
) -> list[Resident]:
    """Get all residents, optionally filtered by unit."""
    query = select(Resident)
    if unit:
        query = query.where(Resident.unit == unit)
    query = query.order_by(Resident.name)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_resident_by_id(
    db: AsyncSession, resident_id: str
) -> Resident | None:
    """Get a single resident by ID."""
    return await db.get(Resident, resident_id)


async def get_high_risk_residents(
    db: AsyncSession, unit: str | None = None
) -> list[Resident]:
    """Get residents with risk_score >= 70, ordered by risk_score descending."""
    query = select(Resident).where(Resident.risk_score >= 70)
    if unit:
        query = query.where(Resident.unit == unit)
    query = query.order_by(desc(Resident.risk_score))

    result = await db.execute(query)
    return list(result.scalars().all())
