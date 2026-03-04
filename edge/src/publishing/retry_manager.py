import asyncio
import random
import logging

logger = logging.getLogger(__name__)

class RetryManager:
    def __init__(self, max_attempts: int = 5, base_delay: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    async def with_retry(self, coro_factory, *args, **kwargs):
        """Retry an async callable with exponential backoff + jitter."""
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await coro_factory(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_attempts:
                    logger.error("All %d retry attempts failed: %s", self.max_attempts, e)
                    raise
                delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                logger.warning("Attempt %d failed, retrying in %.1fs: %s", attempt, delay, e)
                await asyncio.sleep(delay)
