"""Tests for call bell endpoints and edge call bell ingestion."""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from src.core.dependencies import get_db
from src.models.room import Room
from src.models.unit import Unit

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

UNIT_ID = str(uuid.uuid4())
ROOM_ID = str(uuid.uuid4())


@pytest_asyncio.fixture(autouse=True)
async def _seed_room(test_app):
    """Seed a unit and room for call bell tests."""
    get_db_override = test_app.dependency_overrides[get_db]

    async for db in get_db_override():
        existing_unit = await db.get(Unit, UNIT_ID)
        if existing_unit is None:
            db.add(Unit(id=UNIT_ID, name="CB Unit", floor=2))
            await db.flush()

        existing_room = await db.get(Room, ROOM_ID)
        if existing_room is None:
            db.add(
                Room(
                    id=ROOM_ID,
                    number="201",
                    unit_id=UNIT_ID,
                    unit_name="CB Unit",
                    floor=2,
                    status="clear",
                    status_color="green",
                )
            )
        await db.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_get_call_bells_empty(test_client, nurse_token):
    """GET /api/call-bell/ returns 200 with a paginated result."""
    resp = await test_client.get(
        "/api/call-bell/",
        headers={"Authorization": f"Bearer {nurse_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert isinstance(body["data"], list)


async def test_edge_create_callbell(test_client, edge_api_key):
    """POST /api/edge/callbell with a valid API key creates a call bell event (201)."""
    payload = {
        "roomId": ROOM_ID,
        "roomNumber": "201",
        "residentId": str(uuid.uuid4()),
        "residentName": "Jane Doe",
        "unit": "CB Unit",
        "floor": 2,
        "origin": "bedside",
        "priority": "normal",
        "vendor": "jeron",
        "pressedAt": datetime.now(timezone.utc).isoformat(),
    }
    resp = await test_client.post(
        "/api/edge/callbell",
        json=payload,
        headers={"X-API-Key": edge_api_key},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["status"] == "created"
