"""Tests for incident endpoints (GET /api/incidents/)."""

import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_incidents_empty(test_client, admin_token):
    """GET /api/incidents/ returns 200 with a paginated empty result."""
    resp = await test_client.get(
        "/api/incidents/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["total"] == 0
    assert "page" in body
    assert "pageSize" in body
    assert "totalPages" in body


async def test_get_incident_not_found(test_client, admin_token):
    """GET /api/incidents/{random_id} returns 404."""
    random_id = str(uuid.uuid4())
    resp = await test_client.get(
        f"/api/incidents/{random_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
