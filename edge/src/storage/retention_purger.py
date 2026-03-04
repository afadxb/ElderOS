import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class RetentionPurger:
    def __init__(self, base_path: Path, retention_days: int, purge_threshold_percent: int = 90):
        self.base_path = base_path
        self.retention_days = retention_days
        self.purge_threshold = purge_threshold_percent

    async def purge(self):
        """Delete clips older than retention_days. Emergency purge if disk is over threshold."""
        cutoff = time.time() - (self.retention_days * 86400)
        deleted = 0
        for clip_file in sorted(self.base_path.glob("*.mp4")):
            if clip_file.stat().st_mtime < cutoff:
                clip_file.unlink()
                deleted += 1
        if deleted:
            logger.info("Retention purge: deleted %d clips older than %d days", deleted, self.retention_days)

        # Emergency purge if disk is over threshold
        try:
            import psutil
            disk = psutil.disk_usage(str(self.base_path))
            if disk.percent >= self.purge_threshold:
                logger.warning("Disk at %d%%, running emergency purge", disk.percent)
                clips = sorted(self.base_path.glob("*.mp4"), key=lambda f: f.stat().st_mtime)
                for clip in clips[:len(clips) // 4]:  # Delete oldest 25%
                    clip.unlink()
                    deleted += 1
                logger.info("Emergency purge: deleted %d additional clips", deleted)
        except ImportError:
            pass
