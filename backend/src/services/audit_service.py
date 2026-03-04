import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog


async def log_action(
    db: AsyncSession,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Write an audit log entry."""
    entry = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(entry)
    await db.flush()
