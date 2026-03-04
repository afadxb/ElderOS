import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.database import Base
from src.main import create_app
from src.core.dependencies import get_db
from src.core.security import create_access_token, hash_password
from src.models.user import User


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_engine():
    """Async SQLAlchemy engine backed by an in-memory SQLite database."""
    engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    return engine


@pytest_asyncio.fixture
async def test_db(test_engine):
    """Create all tables, yield an async session, then drop all tables.

    Each test gets a clean database.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Application fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def test_app(test_engine):
    """FastAPI test app with the ``get_db`` dependency overridden to use the
    test SQLite engine."""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db
    yield app

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_client(test_app):
    """httpx ``AsyncClient`` wired to the test FastAPI application."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------


async def _seed_user(app, *, user_id: str, name: str, email: str, role: str, unit: str = "Unit A"):
    """Insert a user directly into the test database."""
    get_db_override = app.dependency_overrides[get_db]

    async for db in get_db_override():
        user = User(
            id=user_id,
            name=name,
            email=email,
            password_hash=hash_password("password123"),
            role=role,
            unit=unit,
            avatar_initials=name[:2].upper(),
            is_active=True,
        )
        db.add(user)
        await db.commit()


# ---------------------------------------------------------------------------
# Token fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def admin_token(test_app) -> str:
    """JWT token for a seeded admin user."""
    user_id = str(uuid.uuid4())
    await _seed_user(
        test_app,
        user_id=user_id,
        name="Admin User",
        email="admin@elderos.test",
        role="admin",
    )
    return create_access_token(user_id, "admin")


@pytest_asyncio.fixture
async def nurse_token(test_app) -> str:
    """JWT token for a seeded nurse user."""
    user_id = str(uuid.uuid4())
    await _seed_user(
        test_app,
        user_id=user_id,
        name="Nurse User",
        email="nurse@elderos.test",
        role="nurse",
    )
    return create_access_token(user_id, "nurse")


# ---------------------------------------------------------------------------
# Edge API key fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def edge_api_key() -> str:
    """The edge device shared API key from settings."""
    from src.config import settings
    return settings.edge_api_key
