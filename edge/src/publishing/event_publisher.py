import logging
import uuid
import aiohttp
from src.publishing.event_buffer import EventBuffer
from src.publishing.retry_manager import RetryManager

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, config):
        self.backend_url = config.backend.url
        self.api_key = config.backend.api_key
        self.buffer = EventBuffer()
        self.retry = RetryManager(config.backend.retry_max_attempts, config.backend.retry_base_delay_seconds)
        self._session: aiohttp.ClientSession | None = None

    async def start(self):
        self._session = aiohttp.ClientSession(
            headers={"X-API-Key": self.api_key, "Content-Type": "application/json"}
        )
        await self.buffer.init()

    async def stop(self):
        if self._session:
            await self._session.close()

    async def publish_event(self, event):
        """POST to /api/edge/events. Buffer on failure."""
        payload = event.to_dict()
        try:
            async with self._session.post(f"{self.backend_url}/api/edge/events", json=payload) as resp:
                if resp.status == 200:
                    logger.info("Published event: %s %s", event.event_type, event.room_number)
                    return True
                else:
                    logger.warning("Backend returned %d for event", resp.status)
                    await self.buffer.store(str(uuid.uuid4()), "event", payload)
                    return False
        except Exception as e:
            logger.warning("Failed to publish event: %s", e)
            await self.buffer.store(str(uuid.uuid4()), "event", payload)
            return False

    async def publish_callbell(self, event):
        """POST to /api/edge/callbell."""
        payload = event.to_dict()
        try:
            async with self._session.post(f"{self.backend_url}/api/edge/callbell", json=payload) as resp:
                if resp.status != 200:
                    await self.buffer.store(str(uuid.uuid4()), "callbell", payload)
        except Exception:
            await self.buffer.store(str(uuid.uuid4()), "callbell", payload)

    async def publish_health(self, sensors: list):
        """POST to /api/edge/health."""
        payload = {"sensors": [s.to_dict() for s in sensors]}
        try:
            async with self._session.post(f"{self.backend_url}/api/edge/health", json=payload) as resp:
                if resp.status != 200:
                    logger.warning("Health report failed: %d", resp.status)
        except Exception as e:
            logger.warning("Health report failed: %s", e)

    async def publish_metrics(self, metrics):
        """POST to /api/edge/metrics."""
        payload = metrics.to_dict()
        try:
            async with self._session.post(f"{self.backend_url}/api/edge/metrics", json=payload) as resp:
                if resp.status != 200:
                    logger.warning("Metrics report failed: %d", resp.status)
        except Exception as e:
            logger.warning("Metrics report failed: %s", e)

    async def replay_buffered(self):
        """Replay buffered events on reconnection."""
        events = await self.buffer.get_pending()
        for evt in events:
            endpoint = "/api/edge/events" if evt["event_type"] == "event" else f"/api/edge/{evt['event_type']}"
            try:
                async with self._session.post(f"{self.backend_url}{endpoint}", json=evt["payload"]) as resp:
                    if resp.status == 200:
                        await self.buffer.mark_sent(evt["id"])
            except Exception:
                break  # Backend still down, stop replaying
        await self.buffer.cleanup_sent()
