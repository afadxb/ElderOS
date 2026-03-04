import asyncio
import logging
import os
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

class ClipManager:
    def __init__(self, config):
        self.base_path = Path(config.clip_storage.base_path)
        self.pre_seconds = config.clip_storage.pre_event_seconds
        self.post_seconds = config.clip_storage.post_event_seconds
        self.retention_days = config.clip_storage.retention_days
        self._frame_buffers: dict[str, list] = defaultdict(list)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def add_frame(self, camera_id: str, frame, timestamp: float):
        buf = self._frame_buffers[camera_id]
        buf.append((timestamp, frame))
        max_frames = self.pre_seconds * 10  # ~10 FPS
        if len(buf) > max_frames:
            self._frame_buffers[camera_id] = buf[-max_frames:]

    async def save_clip(self, camera_id: str, event_id: str):
        """Save pre-event frames + capture post-event frames as MP4."""
        clip_path = self.base_path / f"{event_id}.mp4"
        pre_frames = list(self._frame_buffers.get(camera_id, []))
        logger.info("Saving clip for event %s: %d pre-event frames", event_id, len(pre_frames))
        # In production: use cv2.VideoWriter to write frames to MP4
        # For now, create placeholder
        clip_path.touch()
        return str(clip_path)

    def get_clip_path(self, event_id: str) -> str | None:
        clip_path = self.base_path / f"{event_id}.mp4"
        return str(clip_path) if clip_path.exists() else None

    async def run_purger(self):
        """Periodic retention purge loop."""
        from src.storage.retention_purger import RetentionPurger
        purger = RetentionPurger(self.base_path, self.retention_days)
        while True:
            await purger.purge()
            await asyncio.sleep(3600)  # Every hour
