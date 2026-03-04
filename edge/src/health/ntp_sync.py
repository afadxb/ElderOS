import asyncio
import logging
import time

logger = logging.getLogger(__name__)

class NtpSync:
    def __init__(self, config):
        self.server = config.ntp.server
        self.interval = config.ntp.sync_interval_seconds
        self.drift_warn = config.ntp.drift_warn_ms
        self.drift_critical = config.ntp.drift_critical_ms
        self.current_drift_ms: int = 0
        self.sync_status: str = "synced"
        self._last_sync: float = 0

    async def sync_loop(self):
        while True:
            await self._sync()
            await asyncio.sleep(self.interval)

    async def _sync(self):
        try:
            import ntplib
            client = ntplib.NTPClient()
            response = await asyncio.to_thread(client.request, self.server, version=3)
            self.current_drift_ms = int(abs(response.offset) * 1000)
            if self.current_drift_ms < self.drift_warn:
                self.sync_status = "synced"
            elif self.current_drift_ms < self.drift_critical:
                self.sync_status = "drifting"
            else:
                self.sync_status = "lost"
            self._last_sync = time.time()
            logger.debug("NTP sync: drift=%dms status=%s", self.current_drift_ms, self.sync_status)
        except ImportError:
            logger.warning("ntplib not installed, NTP sync disabled")
            self.sync_status = "synced"
            self.current_drift_ms = 0
        except Exception as e:
            logger.warning("NTP sync failed: %s", e)
            if time.time() - self._last_sync > self.interval * 3:
                self.sync_status = "lost"
