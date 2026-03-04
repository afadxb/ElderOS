"""Detect repeat falls within a rolling window.

A fall is considered a "repeat" when the same room has recorded more than
THRESHOLD falls within WINDOW_DAYS.  This flag is surfaced in the event
payload so clinical staff can prioritise care plan reviews.
"""

import time
from collections import defaultdict


class RepeatDetector:
    WINDOW_DAYS = 30
    THRESHOLD = 2

    def __init__(self) -> None:
        self._falls: dict[str, list[float]] = defaultdict(list)

    def check(self, room_id: str, event_type: str) -> bool:
        """Record a fall and return whether it qualifies as a repeat.

        Only 'fall' events are tracked.  Returns True when the room has
        exceeded THRESHOLD falls within the rolling WINDOW_DAYS period.
        """
        if event_type != "fall":
            return False

        now = time.time()
        cutoff = now - (self.WINDOW_DAYS * 86400)
        self._falls[room_id] = [t for t in self._falls[room_id] if t > cutoff]
        self._falls[room_id].append(now)
        return len(self._falls[room_id]) > self.THRESHOLD
