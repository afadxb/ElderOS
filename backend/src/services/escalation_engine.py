import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class EscalationEngine:
    """Background escalation timer engine.

    Loads enabled escalation rules and schedules async timers for each.
    When a timer fires and the event is still unresolved, the event is
    escalated to the next level and an EscalationStep is recorded.
    """

    def __init__(self, session_factory: async_sessionmaker, ws_manager):
        self._timers: dict[str, list[asyncio.Task]] = {}
        self._session_factory = session_factory
        self._ws_manager = ws_manager

    async def start_escalation(self, event_id: str) -> None:
        """Load enabled escalation rules and schedule timers for an event."""
        from src.models.escalation import EscalationRule

        async with self._session_factory() as db:
            result = await db.execute(
                select(EscalationRule)
                .where(EscalationRule.enabled == True)  # noqa: E712
                .order_by(EscalationRule.delay_minutes)
            )
            rules = list(result.scalars().all())

        tasks: list[asyncio.Task] = []
        for i, rule in enumerate(rules):
            task = asyncio.create_task(
                self._escalate_after(event_id, rule, i + 1)
            )
            tasks.append(task)

        self._timers[event_id] = tasks
        logger.info(
            "Started %d escalation timer(s) for event %s", len(tasks), event_id
        )

    async def cancel_escalation(self, event_id: str) -> None:
        """Cancel all pending escalation timers for an event."""
        tasks = self._timers.pop(event_id, [])
        for task in tasks:
            task.cancel()
        if tasks:
            logger.info(
                "Cancelled %d escalation timer(s) for event %s",
                len(tasks),
                event_id,
            )

    async def _escalate_after(self, event_id: str, rule, level: int) -> None:
        """Wait for the rule's delay and then escalate if still needed."""
        try:
            await asyncio.sleep(rule.delay_minutes * 60)
        except asyncio.CancelledError:
            return

        async with self._session_factory() as db:
            from src.models.escalation import EscalationStep
            from src.models.event import Event
            from src.models.incident import Incident

            event = await db.get(Event, event_id)
            if not event or event.status in ("resolved", "dismissed"):
                return

            event.escalation_level = level
            event.status = "escalated"

            # Find or create incident to attach escalation step
            result = await db.execute(
                select(Incident).where(Incident.event_id == event_id)
            )
            incident = result.scalar_one_or_none()
            if incident:
                step = EscalationStep(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    level=level,
                    action=f"{rule.action} to {rule.target}",
                    triggered_at=datetime.now(timezone.utc),
                    acknowledged=False,
                )
                db.add(step)

            await db.commit()
            logger.info(
                "Escalated event %s to level %d: %s -> %s",
                event_id,
                level,
                rule.action,
                rule.target,
            )

            # Notify via WebSocket if manager is available
            if self._ws_manager:
                await self._ws_manager.broadcast(
                    {
                        "type": "escalation",
                        "event_id": event_id,
                        "level": level,
                        "action": rule.action,
                        "target": rule.target,
                    }
                )
