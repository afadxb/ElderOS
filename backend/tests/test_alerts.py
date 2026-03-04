"""Tests for alert endpoints (GET /api/alerts/active, POST ack/resolve)."""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from src.core.dependencies import get_db
from src.models.event import Event
from src.models.room import Room
from src.models.unit import Unit

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

UNIT_ID = str(uuid.uuid4())
ROOM_ID = str(uuid.uuid4())


@pytest_asyncio.fixture(autouse=True)
async def _seed_room(test_app):
    """Seed a unit and room so FK constraints are satisfied."""
    get_db_override = test_app.dependency_overrides[get_db]

    async for db in get_db_override():
        existing_unit = await db.get(Unit, UNIT_ID)
        if existing_unit is None:
            db.add(Unit(id=UNIT_ID, name="Unit A", floor=1))
            await db.flush()

        existing_room = await db.get(Room, ROOM_ID)
        if existing_room is None:
            db.add(
                Room(
                    id=ROOM_ID,
                    number="101",
                    unit_id=UNIT_ID,
                    unit_name="Unit A",
                    floor=1,
                    status="clear",
                    status_color="green",
                )
            )
        await db.commit()


async def _insert_event(test_app, *, status: str = "active") -> str:
    """Insert an event directly and return its id."""
    event_id = str(uuid.uuid4())
    get_db_override = test_app.dependency_overrides[get_db]

    async for db in get_db_override():
        event = Event(
            id=event_id,
            room_id=ROOM_ID,
            room_number="101",
            resident_id=str(uuid.uuid4()),
            resident_name="Test Resident",
            event_type="fall",
            severity="critical",
            confidence="high",
            confidence_score=92,
            status=status,
            detected_at=datetime.now(timezone.utc),
            escalation_level=0,
            pre_event_summary="Motion before fall",
            post_event_state="Still on floor",
            is_repeat_fall=False,
            unit="Unit A",
            sensor_source="ai-vision",
        )
        db.add(event)
        await db.commit()
    return event_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_get_active_alerts_empty(test_client, admin_token):
    """GET /api/alerts/active returns 200 with an empty list when no events exist."""
    resp = await test_client.get(
        "/api/alerts/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_and_get_alert(test_client, test_app, admin_token):
    """After inserting an active event, GET /api/alerts/active returns it."""
    event_id = await _insert_event(test_app, status="active")

    resp = await test_client.get(
        "/api/alerts/active",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    ids = [a["id"] for a in resp.json()]
    assert event_id in ids


async def test_acknowledge_alert(test_client, test_app, nurse_token):
    """POST /{event_id}/acknowledge changes status to acknowledged."""
    event_id = await _insert_event(test_app, status="active")

    # Get the nurse user id from the token
    from src.core.security import decode_token

    payload = decode_token(nurse_token)
    user_id = payload["sub"]

    resp = await test_client.post(
        f"/api/alerts/{event_id}/acknowledge",
        json={"userId": user_id},
        headers={"Authorization": f"Bearer {nurse_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"


async def test_resolve_alert(test_client, test_app, nurse_token):
    """POST /{event_id}/resolve changes status to resolved."""
    event_id = await _insert_event(test_app, status="active")

    from src.core.security import decode_token

    payload = decode_token(nurse_token)
    user_id = payload["sub"]

    resp = await test_client.post(
        f"/api/alerts/{event_id}/resolve",
        json={"userId": user_id},
        headers={"Authorization": f"Bearer {nurse_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"
