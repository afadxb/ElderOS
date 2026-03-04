"""Tests for the EscalationEngine."""

import uuid

import pytest

from src.services.escalation_engine import EscalationEngine

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Minimal stubs
# ---------------------------------------------------------------------------


class _FakeWSManager:
    """Stub WebSocket manager that records broadcasted messages."""

    def __init__(self):
        self.messages: list[dict] = []

    async def broadcast(self, msg: dict):
        self.messages.append(msg)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_escalation_engine_init(test_engine):
    """EscalationEngine initialises correctly with a session factory and WS manager."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    ws = _FakeWSManager()
    engine = EscalationEngine(session_factory, ws)

    assert engine._session_factory is session_factory
    assert engine._ws_manager is ws
    assert engine._timers == {}


async def test_cancel_nonexistent():
    """Cancelling escalation for a non-existent event does not raise."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    dummy_engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    session_factory = async_sessionmaker(
        dummy_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    ws = _FakeWSManager()
    esc = EscalationEngine(session_factory, ws)

    # Should not raise
    await esc.cancel_escalation(str(uuid.uuid4()))

    await dummy_engine.dispose()
