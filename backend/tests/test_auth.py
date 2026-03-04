"""Tests for authentication endpoints (POST /api/auth/login, GET /api/auth/me)."""

import uuid

import pytest
import pytest_asyncio

from src.core.dependencies import get_db
from src.core.security import hash_password
from src.models.user import User

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AUTH_USER_ID = str(uuid.uuid4())
AUTH_EMAIL = "authtest@elderos.test"
AUTH_PASSWORD = "correcthorsebattery"


@pytest_asyncio.fixture(autouse=True)
async def _seed_auth_user(test_app):
    """Insert a known user for the auth tests."""
    get_db_override = test_app.dependency_overrides[get_db]

    async for db in get_db_override():
        existing = await db.get(User, AUTH_USER_ID)
        if existing is None:
            user = User(
                id=AUTH_USER_ID,
                name="Auth Test User",
                email=AUTH_EMAIL,
                password_hash=hash_password(AUTH_PASSWORD),
                role="nurse",
                unit="Unit A",
                avatar_initials="AT",
                is_active=True,
            )
            db.add(user)
            await db.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_login_success(test_client):
    """POST /api/auth/login with valid credentials returns 200 and a token."""
    resp = await test_client.post(
        "/api/auth/login",
        json={"email": AUTH_EMAIL, "password": AUTH_PASSWORD},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "token" in body
    assert body["user"]["email"] == AUTH_EMAIL


async def test_login_wrong_password(test_client):
    """POST /api/auth/login with wrong password returns 401."""
    resp = await test_client.post(
        "/api/auth/login",
        json={"email": AUTH_EMAIL, "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(test_client):
    """POST /api/auth/login with unknown email returns 401."""
    resp = await test_client.post(
        "/api/auth/login",
        json={"email": "nobody@elderos.test", "password": "irrelevant"},
    )
    assert resp.status_code == 401


async def test_get_me(test_client):
    """GET /api/auth/me with a valid token returns user data."""
    # Login first to obtain a valid token
    login_resp = await test_client.post(
        "/api/auth/login",
        json={"email": AUTH_EMAIL, "password": AUTH_PASSWORD},
    )
    token = login_resp.json()["token"]

    resp = await test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == AUTH_EMAIL
    assert body["role"] == "nurse"


async def test_get_me_no_token(test_client):
    """GET /api/auth/me without a token returns 401."""
    resp = await test_client.get("/api/auth/me")
    assert resp.status_code == 401
