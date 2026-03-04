import json
import aiosqlite
from datetime import datetime, timezone

class EventBuffer:
    def __init__(self, db_path: str = "/data/edge_buffer.db"):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS buffered_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    sent INTEGER DEFAULT 0
                )
            """)
            await db.commit()

    async def store(self, event_id: str, event_type: str, payload: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO buffered_events (id, event_type, payload, created_at) VALUES (?, ?, ?, ?)",
                (event_id, event_type, json.dumps(payload), datetime.now(timezone.utc).isoformat())
            )
            await db.commit()

    async def get_pending(self, limit: int = 100) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM buffered_events WHERE sent = 0 ORDER BY created_at LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [{"id": r["id"], "event_type": r["event_type"], "payload": json.loads(r["payload"])} for r in rows]

    async def mark_sent(self, event_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE buffered_events SET sent = 1 WHERE id = ?", (event_id,))
            await db.commit()

    async def cleanup_sent(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM buffered_events WHERE sent = 1")
            await db.commit()
