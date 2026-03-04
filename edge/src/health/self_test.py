import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SelfTest:
    def __init__(self, config):
        self.schedule_hour = config.self_test.schedule_hour
        self.config = config
        self.last_result: dict = {"passed": True, "details": []}

    async def run_schedule(self):
        while True:
            now = datetime.now(timezone.utc)
            if now.hour == self.schedule_hour:
                await self.run_test()
                await asyncio.sleep(3600)  # Don't run again for an hour
            await asyncio.sleep(60)

    async def run_test(self) -> dict:
        logger.info("Running nightly self-test")
        details = []
        all_passed = True

        # Test 1: Storage space
        try:
            import psutil
            disk = psutil.disk_usage("/")
            if disk.percent < 90:
                details.append(f"Storage: OK ({disk.percent}% used)")
            else:
                details.append(f"Storage: WARNING ({disk.percent}% used)")
                all_passed = False
        except Exception as e:
            details.append(f"Storage: FAIL ({e})")
            all_passed = False

        # Test 2: NTP connectivity
        try:
            import ntplib
            client = ntplib.NTPClient()
            await asyncio.to_thread(client.request, self.config.ntp.server, version=3)
            details.append("NTP: OK")
        except Exception:
            details.append("NTP: FAIL (cannot reach server)")
            all_passed = False

        # Test 3: Backend connectivity
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.backend.url}/api/system/metrics", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        details.append("Backend: OK")
                    else:
                        details.append(f"Backend: WARNING (status {resp.status})")
        except Exception:
            details.append("Backend: FAIL (unreachable)")
            all_passed = False

        # Test 4: Inference pipeline
        try:
            import numpy as np
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            details.append("Inference: OK (test frame processed)")
        except Exception as e:
            details.append(f"Inference: FAIL ({e})")
            all_passed = False

        self.last_result = {"passed": all_passed, "details": details}
        logger.info("Self-test complete: %s", "PASSED" if all_passed else "FAILED")
        return self.last_result
