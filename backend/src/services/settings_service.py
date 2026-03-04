from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.escalation import EscalationRule
from src.models.settings import ConfidenceThreshold, ExclusionZone, RetentionPolicy


# ---------------------------------------------------------------------------
# Escalation rules
# ---------------------------------------------------------------------------


async def get_all_escalation_rules(db: AsyncSession) -> list[EscalationRule]:
    """Get all escalation rules ordered by delay."""
    result = await db.execute(
        select(EscalationRule).order_by(EscalationRule.delay_minutes)
    )
    return list(result.scalars().all())


async def update_escalation_rule(
    db: AsyncSession, rule_id: str, updates: dict
) -> EscalationRule | None:
    """Update a single escalation rule by ID."""
    rule = await db.get(EscalationRule, rule_id)
    if not rule:
        return None

    allowed = {"delay_minutes", "action", "target", "enabled"}
    for key, value in updates.items():
        if key in allowed:
            setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)
    return rule


# ---------------------------------------------------------------------------
# Confidence thresholds (singleton row, id=1)
# ---------------------------------------------------------------------------


async def get_confidence_thresholds(db: AsyncSession) -> ConfidenceThreshold:
    """Get confidence thresholds. Creates default row if missing."""
    row = await db.get(ConfidenceThreshold, 1)
    if not row:
        row = ConfidenceThreshold(id=1, high_min=85, medium_min=60, low_min=30)
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row


async def update_confidence_thresholds(
    db: AsyncSession, high_min: int, medium_min: int, low_min: int
) -> ConfidenceThreshold:
    """Update confidence threshold values."""
    row = await get_confidence_thresholds(db)
    row.high_min = high_min
    row.medium_min = medium_min
    row.low_min = low_min
    await db.commit()
    await db.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Retention policy (singleton row, id=1)
# ---------------------------------------------------------------------------


async def get_retention_policy(db: AsyncSession) -> RetentionPolicy:
    """Get retention policy. Creates default row if missing."""
    row = await db.get(RetentionPolicy, 1)
    if not row:
        row = RetentionPolicy(
            id=1,
            clip_retention_days=7,
            metadata_retention_days=90,
            auto_purge_enabled=True,
            purge_threshold_percent=90,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row


async def update_retention_policy(
    db: AsyncSession,
    clip_retention_days: int,
    metadata_retention_days: int,
    auto_purge_enabled: bool,
    purge_threshold_percent: int,
) -> RetentionPolicy:
    """Update retention policy values."""
    row = await get_retention_policy(db)
    row.clip_retention_days = clip_retention_days
    row.metadata_retention_days = metadata_retention_days
    row.auto_purge_enabled = auto_purge_enabled
    row.purge_threshold_percent = purge_threshold_percent
    await db.commit()
    await db.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Exclusion zones
# ---------------------------------------------------------------------------


async def get_all_exclusion_zones(db: AsyncSession) -> list[ExclusionZone]:
    """Get all exclusion zones."""
    result = await db.execute(
        select(ExclusionZone).order_by(ExclusionZone.room_number)
    )
    return list(result.scalars().all())


async def update_exclusion_zone(
    db: AsyncSession, zone_id: str, updates: dict
) -> ExclusionZone | None:
    """Update a single exclusion zone by ID."""
    zone = await db.get(ExclusionZone, zone_id)
    if not zone:
        return None

    allowed = {"room_id", "room_number", "zone_name", "enabled"}
    for key, value in updates.items():
        if key in allowed:
            setattr(zone, key, value)

    await db.commit()
    await db.refresh(zone)
    return zone
