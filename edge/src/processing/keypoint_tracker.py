"""Temporal keypoint tracker with EMA smoothing and sliding window buffer.

Smooths noisy per-frame keypoint detections using exponential moving average
and maintains a time-windowed history of poses for rule evaluation.
"""

import logging
from collections import deque
from dataclasses import dataclass

import numpy as np

from src.models.keypoints import PoseKeypoints, NUM_KEYPOINTS

logger = logging.getLogger(__name__)


@dataclass
class TrackerConfig:
    """Configuration for the keypoint tracker."""

    ema_alpha: float = 0.4  # Smoothing factor: 0=full history, 1=no smoothing
    window_seconds: float = 5.0  # How many seconds of history to retain
    min_confidence: float = 0.3  # Ignore keypoints below this confidence


class KeypointTracker:
    """Per-person keypoint tracker with EMA smoothing.

    Maintains a smoothed pose estimate and a temporal buffer of recent
    poses for rule evaluation (e.g., sustained states, velocity).
    """

    def __init__(self, person_id: int = 0, config: TrackerConfig | None = None) -> None:
        self.person_id = person_id
        self.config = config or TrackerConfig()
        self._smoothed_xy: np.ndarray | None = None  # (17, 2)
        self._history: deque[PoseKeypoints] = deque()

    def update(self, pose: PoseKeypoints) -> PoseKeypoints:
        """Ingest a raw pose and return the EMA-smoothed version.

        Args:
            pose: Raw keypoint detection from the current frame.

        Returns:
            Smoothed PoseKeypoints with the same timestamp.
        """
        alpha = self.config.ema_alpha
        min_conf = self.config.min_confidence

        if self._smoothed_xy is None:
            # First frame — initialise directly
            self._smoothed_xy = pose.xy.copy()
        else:
            # Per-keypoint EMA: only update keypoints with sufficient confidence
            for i in range(NUM_KEYPOINTS):
                if pose.confidence[i] >= min_conf:
                    self._smoothed_xy[i] = (
                        alpha * pose.xy[i] + (1 - alpha) * self._smoothed_xy[i]
                    )

        smoothed = PoseKeypoints(
            xy=self._smoothed_xy.copy(),
            confidence=pose.confidence.copy(),
            timestamp=pose.timestamp,
            person_id=self.person_id,
        )

        # Add to history and prune old entries
        self._history.append(smoothed)
        self._prune_history(pose.timestamp)

        return smoothed

    def get_history(self) -> list[PoseKeypoints]:
        """Return the full pose history within the time window."""
        return list(self._history)

    def get_latest(self) -> PoseKeypoints | None:
        """Return the most recent smoothed pose, or None if no data."""
        return self._history[-1] if self._history else None

    def get_pose_at_offset(self, seconds_ago: float) -> PoseKeypoints | None:
        """Return the pose closest to N seconds before the latest pose.

        Useful for computing velocity (e.g., hip height change over 0.5s).
        """
        if not self._history:
            return None
        target_time = self._history[-1].timestamp - seconds_ago
        best: PoseKeypoints | None = None
        best_diff = float("inf")
        for pose in self._history:
            diff = abs(pose.timestamp - target_time)
            if diff < best_diff:
                best_diff = diff
                best = pose
        return best

    def hip_height_velocity(
        self, frame_height: int, interval_seconds: float = 0.5
    ) -> float | None:
        """Compute the rate of change in hip height over a time interval.

        Returns:
            Positive value = hips moving downward (falling).
            Negative value = hips moving upward (standing).
            None if insufficient history.
        """
        current = self.get_latest()
        past = self.get_pose_at_offset(interval_seconds)
        if current is None or past is None:
            return None

        current_h = current.hip_height_normalized(frame_height)
        past_h = past.hip_height_normalized(frame_height)
        dt = current.timestamp - past.timestamp
        if dt <= 0:
            return None

        # Positive = downward movement (hip_height_normalized increases)
        return (current_h - past_h) / dt

    def seconds_in_history(self) -> float:
        """How many seconds of pose history are currently buffered."""
        if len(self._history) < 2:
            return 0.0
        return self._history[-1].timestamp - self._history[0].timestamp

    def reset(self) -> None:
        """Clear all state."""
        self._smoothed_xy = None
        self._history.clear()

    def _prune_history(self, current_time: float) -> None:
        cutoff = current_time - self.config.window_seconds
        while self._history and self._history[0].timestamp < cutoff:
            self._history.popleft()


class MultiPersonTracker:
    """Manages KeypointTracker instances for multiple detected persons."""

    def __init__(self, config: TrackerConfig | None = None) -> None:
        self.config = config or TrackerConfig()
        self._trackers: dict[int, KeypointTracker] = {}

    def update(self, person_id: int, pose: PoseKeypoints) -> PoseKeypoints:
        if person_id not in self._trackers:
            self._trackers[person_id] = KeypointTracker(person_id, self.config)
        return self._trackers[person_id].update(pose)

    def get_tracker(self, person_id: int) -> KeypointTracker | None:
        return self._trackers.get(person_id)

    def active_ids(self) -> list[int]:
        return list(self._trackers.keys())

    def remove_stale(self, current_time: float, timeout_seconds: float = 10.0) -> None:
        """Remove trackers that haven't received updates recently."""
        stale = [
            pid
            for pid, tracker in self._trackers.items()
            if tracker.get_latest() is not None
            and (current_time - tracker.get_latest().timestamp) > timeout_seconds
        ]
        for pid in stale:
            del self._trackers[pid]
