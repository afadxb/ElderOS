"""Pose-based event processor that bridges pose detection to the existing pipeline.

Orchestrates: CameraFrame -> PoseDetector -> KeypointTracker -> PoseRulesEngine -> Detection
Then forwards Detections to the standard EventProcessor for fusion/scoring/publishing.
"""

import logging

from src.inference.pose_detector import PoseDetector
from src.inference.base_detector import Detection
from src.processing.keypoint_tracker import KeypointTracker, MultiPersonTracker, TrackerConfig
from src.processing.pose_rules_engine import PoseRulesEngine, PoseRulesConfig
from src.processing.zone_geometry import BedZone

logger = logging.getLogger(__name__)


class PoseEventProcessor:
    """Processes camera frames through pose estimation and rule evaluation.

    One instance per camera/room. Produces Detection objects that are
    compatible with the existing EventProcessor.process_vision_event().
    """

    def __init__(
        self,
        room_id: str,
        pose_detector: PoseDetector,
        bed_zone: BedZone | None = None,
        rules_config: PoseRulesConfig | None = None,
        tracker_config: TrackerConfig | None = None,
    ) -> None:
        self.room_id = room_id
        self.pose_detector = pose_detector
        self.tracker = MultiPersonTracker(tracker_config or TrackerConfig())
        self.rules_engine = PoseRulesEngine(bed_zone=bed_zone, config=rules_config)
        self._frame_count = 0

    def process_frame(self, frame, timestamp: float) -> list[Detection]:
        """Process a single camera frame through the full pose pipeline.

        Args:
            frame: BGR numpy array from camera.
            timestamp: monotonic time in seconds.

        Returns:
            List of Detection objects for events detected this frame.
        """
        self._frame_count += 1

        # Step 1: Pose estimation
        poses = self.pose_detector.detect(frame, timestamp)
        if not poses:
            return []

        all_detections: list[Detection] = []

        for raw_pose in poses:
            # Step 2: Smooth keypoints
            smoothed = self.tracker.update(raw_pose.person_id, raw_pose)

            # Step 3: Evaluate rules against smoothed pose
            # Use the per-person tracker for temporal analysis
            person_tracker = self.tracker.get_tracker(raw_pose.person_id)
            if person_tracker is None:
                continue

            detections = self.rules_engine.evaluate(person_tracker)
            all_detections.extend(detections)

        # Cleanup stale person trackers
        self.tracker.remove_stale(timestamp)

        return all_detections

    @property
    def frame_count(self) -> int:
        return self._frame_count
