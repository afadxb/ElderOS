"""Device config synchronization — fetches device configs from the backend API.

Runs periodically so the edge device picks up camera/sensor changes made via
the dashboard without restarting the edge service.
"""

import asyncio
import logging
from dataclasses import dataclass, field

import aiohttp

logger = logging.getLogger(__name__)

DEFAULT_SYNC_INTERVAL = 120  # seconds


@dataclass
class DeviceConfig:
    """A single device config received from the backend."""

    sensor_id: str
    room_id: str
    room_number: str | None
    type: str | None
    name: str | None
    connection_config: dict | None = None
    detection_config: dict | None = None


class ConfigSync:
    """Periodically fetches device configs from the backend and exposes them."""

    def __init__(
        self,
        edge_device_id: str,
        backend_url: str = "http://backend:8000",
        api_key: str = "edge-device-shared-secret",
        sync_interval: int = DEFAULT_SYNC_INTERVAL,
    ) -> None:
        self._edge_device_id = edge_device_id
        self._backend_url = backend_url.rstrip("/")
        self._api_key = api_key
        self._sync_interval = sync_interval
        self._running = False
        self._devices: list[DeviceConfig] = []

    @property
    def devices(self) -> list[DeviceConfig]:
        return list(self._devices)

    def get_cameras(self) -> list[DeviceConfig]:
        return [d for d in self._devices if d.type == "ai-vision"]

    def get_radars(self) -> list[DeviceConfig]:
        return [d for d in self._devices if d.type == "ai-sensor"]

    async def sync_once(self) -> int:
        """Fetch device configs from backend. Returns the number of devices loaded."""
        url = f"{self._backend_url}/api/edge/config"
        headers = {"X-API-Key": self._api_key}
        params = {"edge_device_id": self._edge_device_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        logger.warning("Config sync failed: HTTP %d", resp.status)
                        return 0
                    data = await resp.json()
        except Exception as e:
            logger.warning("Config sync error: %s", e)
            return 0

        devices_data = data.get("devices", [])
        self._devices = [
            DeviceConfig(
                sensor_id=d.get("sensorId", d.get("sensor_id", "")),
                room_id=d.get("roomId", d.get("room_id", "")),
                room_number=d.get("roomNumber", d.get("room_number")),
                type=d.get("type"),
                name=d.get("name"),
                connection_config=d.get("connectionConfig", d.get("connection_config")),
                detection_config=d.get("detectionConfig", d.get("detection_config")),
            )
            for d in devices_data
        ]

        if self._devices:
            logger.info(
                "Config sync: loaded %d device(s) from backend", len(self._devices)
            )
        return len(self._devices)

    async def run(self) -> None:
        """Run the sync loop. Call this as a background asyncio task."""
        self._running = True
        logger.info(
            "Config sync started (edge_device_id=%s, interval=%ds)",
            self._edge_device_id,
            self._sync_interval,
        )

        while self._running:
            await self.sync_once()
            await asyncio.sleep(self._sync_interval)

    def stop(self) -> None:
        self._running = False
