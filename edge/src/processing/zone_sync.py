"""Zone synchronization — fetches bed-zone polygons from the backend API.

Runs periodically to pick up zone changes made via the dashboard or
calibration tool without restarting the edge service.
"""

import asyncio
import logging

import aiohttp

from src.processing.zone_geometry import BedZone, ZoneManager

logger = logging.getLogger(__name__)

DEFAULT_SYNC_INTERVAL = 60  # seconds


class ZoneSync:
    """Periodically fetches zone data from the backend and updates ZoneManager."""

    def __init__(
        self,
        zone_manager: ZoneManager,
        backend_url: str = "http://backend:8000",
        api_key: str = "edge-device-shared-secret",
        sync_interval: int = DEFAULT_SYNC_INTERVAL,
    ) -> None:
        self._zone_manager = zone_manager
        self._backend_url = backend_url.rstrip("/")
        self._api_key = api_key
        self._sync_interval = sync_interval
        self._running = False

    async def sync_once(self) -> int:
        """Fetch all zones from backend and update the ZoneManager.

        Returns the number of zones loaded.
        """
        url = f"{self._backend_url}/api/rooms/zones/all"
        headers = {"X-API-Key": self._api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        logger.warning("Zone sync failed: HTTP %d", resp.status)
                        return 0

                    zones_data = await resp.json()
        except Exception as e:
            logger.warning("Zone sync error: %s", e)
            return 0

        count = 0
        for z in zones_data:
            room_id = z.get("room_id")
            vertices = z.get("vertices")
            if room_id and vertices and len(vertices) >= 3:
                zone = BedZone(
                    room_id=room_id,
                    vertices=[tuple(v) for v in vertices],
                    label=z.get("label", "bed"),
                )
                self._zone_manager.add_zone(zone)
                count += 1

        if count:
            logger.info("Zone sync: loaded %d zone(s) from backend", count)
        return count

    async def run(self) -> None:
        """Run the sync loop. Call this as a background asyncio task."""
        self._running = True
        logger.info("Zone sync started (interval=%ds)", self._sync_interval)

        while self._running:
            await self.sync_once()
            await asyncio.sleep(self._sync_interval)

    def stop(self) -> None:
        self._running = False
