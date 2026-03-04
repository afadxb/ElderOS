from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.incident import Incident
from src.models.user import User
from src.schemas.common import PaginatedResponse
from src.schemas.incident import IncidentResponse
from src.utils.pagination import paginate

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[IncidentResponse])
async def get_incidents(
    unit: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENTS_VIEW)),
):
    """Get paginated incidents with optional filters."""
    query = (
        select(Incident)
        .options(selectinload(Incident.escalation_steps))
        .order_by(desc(Incident.detected_at))
    )
    if unit:
        query = query.where(Incident.unit == unit)
    if event_type:
        query = query.where(Incident.event_type == event_type)
    if status:
        query = query.where(Incident.status == status)

    result = await paginate(db, query, page, page_size)
    result["data"] = [
        IncidentResponse.model_validate(i) for i in result["data"]
    ]
    return result


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENTS_VIEW)),
):
    """Get a single incident with escalation timeline."""
    query = (
        select(Incident)
        .options(selectinload(Incident.escalation_steps))
        .where(Incident.id == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalars().unique().one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@router.get("/resident/{resident_id}", response_model=list[IncidentResponse])
async def get_incidents_by_resident(
    resident_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENTS_VIEW)),
):
    """Get all incidents for a specific resident."""
    query = (
        select(Incident)
        .options(selectinload(Incident.escalation_steps))
        .where(Incident.resident_id == resident_id)
        .order_by(desc(Incident.detected_at))
    )
    result = await db.execute(query)
    incidents = list(result.scalars().unique().all())
    return [IncidentResponse.model_validate(i) for i in incidents]
