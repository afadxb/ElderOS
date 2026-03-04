from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.settings import (
    ConfidenceThresholdsResponse,
    ConfidenceThresholdsUpdate,
    EscalationRuleResponse,
    EscalationRuleUpdate,
    ExclusionZoneResponse,
    ExclusionZoneUpdate,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
)
from src.services import settings_service, audit_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Escalation Rules
# ---------------------------------------------------------------------------


@router.get("/escalation-rules", response_model=list[EscalationRuleResponse])
async def get_escalation_rules(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_VIEW)),
):
    """Get all escalation rules."""
    rules = await settings_service.get_escalation_rules(db)
    return [EscalationRuleResponse.model_validate(r) for r in rules]


@router.put("/escalation-rules", response_model=list[EscalationRuleResponse])
async def update_escalation_rules(
    body: list[EscalationRuleUpdate],
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update escalation rules (full replacement)."""
    rules = await settings_service.update_escalation_rules(db, body)
    await audit_service.log_action(
        db, user.id, "update", "escalation_rules", "all",
        details={"count": len(body)},
    )
    await db.commit()
    return [EscalationRuleResponse.model_validate(r) for r in rules]


# ---------------------------------------------------------------------------
# Confidence Thresholds
# ---------------------------------------------------------------------------


@router.get("/confidence-thresholds", response_model=ConfidenceThresholdsResponse)
async def get_confidence_thresholds(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_VIEW)),
):
    """Get current confidence thresholds."""
    thresholds = await settings_service.get_confidence_thresholds(db)
    return ConfidenceThresholdsResponse.model_validate(thresholds)


@router.put("/confidence-thresholds", response_model=ConfidenceThresholdsResponse)
async def update_confidence_thresholds(
    body: ConfidenceThresholdsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update confidence thresholds."""
    thresholds = await settings_service.update_confidence_thresholds(db, body)
    await audit_service.log_action(
        db, user.id, "update", "confidence_thresholds", "1",
        details=body.model_dump(),
    )
    await db.commit()
    return ConfidenceThresholdsResponse.model_validate(thresholds)


# ---------------------------------------------------------------------------
# Retention Policy
# ---------------------------------------------------------------------------


@router.get("/retention-policy", response_model=RetentionPolicyResponse)
async def get_retention_policy(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_VIEW)),
):
    """Get current data retention policy."""
    policy = await settings_service.get_retention_policy(db)
    return RetentionPolicyResponse.model_validate(policy)


@router.put("/retention-policy", response_model=RetentionPolicyResponse)
async def update_retention_policy(
    body: RetentionPolicyUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update data retention policy."""
    policy = await settings_service.update_retention_policy(db, body)
    await audit_service.log_action(
        db, user.id, "update", "retention_policy", "1",
        details=body.model_dump(),
    )
    await db.commit()
    return RetentionPolicyResponse.model_validate(policy)


# ---------------------------------------------------------------------------
# Exclusion Zones
# ---------------------------------------------------------------------------


@router.get("/exclusion-zones", response_model=list[ExclusionZoneResponse])
async def get_exclusion_zones(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_VIEW)),
):
    """Get all exclusion zones."""
    zones = await settings_service.get_exclusion_zones(db)
    return [ExclusionZoneResponse.model_validate(z) for z in zones]


@router.put("/exclusion-zones/{zone_id}", response_model=ExclusionZoneResponse)
async def update_exclusion_zone(
    zone_id: str,
    body: ExclusionZoneUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update a single exclusion zone."""
    zone = await settings_service.update_exclusion_zone(db, zone_id, body)
    if not zone:
        raise HTTPException(status_code=404, detail="Exclusion zone not found")
    await audit_service.log_action(
        db, user.id, "update", "exclusion_zone", zone_id,
        details=body.model_dump(),
    )
    await db.commit()

    # Broadcast data change so rooms refresh exclusion zone status
    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast_data_change([["rooms"]])

    return ExclusionZoneResponse.model_validate(zone)
