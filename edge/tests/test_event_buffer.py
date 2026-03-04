"""Tests for the SQLite event buffer."""

import os
import tempfile
import uuid

import pytest
import pytest_asyncio

from src.publishing.event_buffer import EventBuffer

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def buffer():
    """Create an EventBuffer backed by a temporary SQLite file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    buf = EventBuffer(db_path=tmp.name)
    await buf.init()
    yield buf
    os.unlink(tmp.name)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_buffer_store_and_retrieve(buffer: EventBuffer):
    """Storing an event and then retrieving pending returns it."""
    event_id = str(uuid.uuid4())
    payload = {"room_id": "room-1", "event_type": "fall"}

    await buffer.store(event_id, "fall", payload)
    pending = await buffer.get_pending()

    assert len(pending) == 1
    assert pending[0]["id"] == event_id
    assert pending[0]["event_type"] == "fall"
    assert pending[0]["payload"] == payload


async def test_buffer_mark_sent(buffer: EventBuffer):
    """After marking an event as sent it no longer appears in pending."""
    event_id = str(uuid.uuid4())
    await buffer.store(event_id, "bed-exit", {"data": "test"})

    # Confirm it is pending
    pending = await buffer.get_pending()
    assert len(pending) == 1

    # Mark sent
    await buffer.mark_sent(event_id)

    # No longer pending
    pending = await buffer.get_pending()
    assert len(pending) == 0


async def test_buffer_cleanup_sent(buffer: EventBuffer):
    """cleanup_sent removes all events that have been marked as sent."""
    id1 = str(uuid.uuid4())
    id2 = str(uuid.uuid4())

    await buffer.store(id1, "fall", {"a": 1})
    await buffer.store(id2, "fall", {"b": 2})

    await buffer.mark_sent(id1)
    await buffer.cleanup_sent()

    # Only unsent event remains pending
    pending = await buffer.get_pending()
    assert len(pending) == 1
    assert pending[0]["id"] == id2


async def test_buffer_duplicate_store(buffer: EventBuffer):
    """Storing the same event_id twice (INSERT OR IGNORE) does not duplicate."""
    event_id = str(uuid.uuid4())
    await buffer.store(event_id, "fall", {"x": 1})
    await buffer.store(event_id, "fall", {"x": 1})

    pending = await buffer.get_pending()
    assert len(pending) == 1
