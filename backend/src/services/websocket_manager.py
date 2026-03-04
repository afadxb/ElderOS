import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages connected WebSocket clients and broadcasts messages."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        logger.info("WebSocket client connected. Total: %d", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)
        logger.info("WebSocket client disconnected. Total: %d", len(self._connections))

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def broadcast_alert(self, alert_data: dict) -> None:
        """Broadcast a new alert event to all connected clients."""
        msg = json.dumps({"type": "alert", "data": alert_data})
        await self._broadcast(msg)

    async def broadcast_system_update(self) -> None:
        """Notify all clients to refresh system data."""
        await self._broadcast(json.dumps({"type": "system_update"}))

    async def broadcast_data_change(self, query_keys: list[list[str]]) -> None:
        """Notify clients to invalidate specific query caches."""
        await self._broadcast(json.dumps({"type": "data_change", "queryKeys": query_keys}))

    async def _broadcast(self, message: str) -> None:
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
