import asyncio
import logging
import json
from datetime import datetime, timezone
from src.models.events import CallBellPayload

logger = logging.getLogger(__name__)

class CallBellListener:
    def __init__(self, callbell_config, event_publisher):
        self.config = callbell_config
        self.publisher = event_publisher
        self._running = False

    async def run(self):
        self._running = True
        logger.info("Starting call bell listener: %s:%d (%s)", self.config.host, self.config.port, self.config.vendor)
        while self._running:
            try:
                reader, writer = await asyncio.open_connection(self.config.host, self.config.port)
                logger.info("Connected to nurse call system")
                while self._running:
                    data = await reader.read(4096)
                    if not data:
                        break
                    events = self._parse_vendor_protocol(data)
                    for event in events:
                        await self.publisher.publish_callbell(event)
            except ConnectionRefusedError:
                logger.warning("Cannot connect to nurse call system at %s:%d", self.config.host, self.config.port)
            except Exception as e:
                logger.error("Call bell listener error: %s", e)
            await asyncio.sleep(10)

    def _parse_vendor_protocol(self, data: bytes) -> list[CallBellPayload]:
        """Route to vendor-specific parser."""
        if self.config.vendor == "jeron":
            return self._parse_jeron(data)
        elif self.config.vendor == "rauland":
            return self._parse_rauland(data)
        elif self.config.vendor == "hill-rom":
            return self._parse_hillrom(data)
        return []

    def _parse_jeron(self, data: bytes) -> list[CallBellPayload]:
        """Parse Jeron nurse call protocol. Stub -- real implementation depends on Jeron API docs."""
        events = []
        try:
            # Jeron systems typically send JSON or structured text
            text = data.decode("utf-8", errors="ignore").strip()
            for line in text.split("\n"):
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    events.append(CallBellPayload(
                        room_id=msg.get("room_id", ""),
                        room_number=msg.get("room", ""),
                        resident_id=msg.get("resident_id", ""),
                        resident_name=msg.get("resident_name", ""),
                        unit=msg.get("unit", ""),
                        floor=msg.get("floor", 1),
                        origin=msg.get("origin", "bedside"),
                        priority=msg.get("priority", "normal"),
                        vendor="jeron",
                        pressed_at=datetime.now(timezone.utc).isoformat(),
                    ))
                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception:
            pass
        return events

    def _parse_rauland(self, data: bytes) -> list[CallBellPayload]:
        """Parse Rauland Responder protocol. Stub."""
        # Rauland uses proprietary binary protocol
        return self._parse_jeron(data)  # Fallback to JSON parsing

    def _parse_hillrom(self, data: bytes) -> list[CallBellPayload]:
        """Parse Hill-Rom Nurse Call protocol. Stub."""
        return self._parse_jeron(data)  # Fallback to JSON parsing

    def stop(self):
        self._running = False
