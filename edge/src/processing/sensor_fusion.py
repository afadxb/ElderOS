"""Sensor fusion with a sliding time window.

When both vision and radar report the same event type for the same room
within the configured window, the event is considered "fused" and receives
a confidence boost.
"""

import time

from src.inference.base_detector import Detection


class SensorFusion:
    def __init__(self, config) -> None:
        self.window = config.fusion.time_window_seconds
        self.boost = config.fusion.confidence_boost
        self._pending: dict[str, list[tuple[float, str, Detection]]] = {}

    def try_fuse(self, room_id: str, source: str, detection: Detection) -> bool:
        """Attempt to fuse a detection with a pending detection from another source.

        Args:
            room_id: Room the detection originated from.
            source: Source identifier ('vision' or 'radar').
            detection: The detection to try fusing.

        Returns:
            True if the detection was fused with a complementary source.
        """
        now = time.time()

        # Prune expired entries
        pending = self._pending.get(room_id, [])
        pending = [(t, s, d) for t, s, d in pending if now - t < self.window]

        # Check for a matching detection from a different source
        for t, s, d in pending:
            if s != source and d.event_type == detection.event_type:
                # Fused -- clear pending for this room
                self._pending[room_id] = []
                return True

        # No match yet -- park this detection
        pending.append((now, source, detection))
        self._pending[room_id] = pending
        return False
