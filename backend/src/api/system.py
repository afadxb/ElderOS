from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.system import (
    SelfTestResponse,
    SensorHealthResponse,
    SystemMetricsResponse,
)
from src.services import system_service

router = APIRouter()


@router.get("/sensors", response_model=list[SensorHealthResponse])
async def get_sensors(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_VIEW)),
):
    """Get health status for all sensors."""
    sensors = await system_service.get_sensor_health(db)
    return [SensorHealthResponse.model_validate(s) for s in sensors]


@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_VIEW)),
):
    """Get current system metrics (CPU, memory, disk, NTP)."""
    metrics = await system_service.get_latest_metrics(db)
    return SystemMetricsResponse.model_validate(metrics)


@router.get("/self-test", response_model=SelfTestResponse)
async def run_self_test(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SYSTEM_VIEW)),
):
    """Run a system self-test and return results."""
    result = await system_service.run_self_test(db)
    return SelfTestResponse.model_validate(result)
