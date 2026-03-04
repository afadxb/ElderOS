"""COCO 17-keypoint pose data model for TRT-Pose / BodyPoseNet output."""

from dataclasses import dataclass, field
import numpy as np


# COCO 17-keypoint indices
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_ELBOW = 7
RIGHT_ELBOW = 8
LEFT_WRIST = 9
RIGHT_WRIST = 10
LEFT_HIP = 11
RIGHT_HIP = 12
LEFT_KNEE = 13
RIGHT_KNEE = 14
LEFT_ANKLE = 15
RIGHT_ANKLE = 16

NUM_KEYPOINTS = 17

# Semantic groups for rule evaluation
TORSO_KEYPOINTS = (LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP)
HIP_KEYPOINTS = (LEFT_HIP, RIGHT_HIP)
SHOULDER_KEYPOINTS = (LEFT_SHOULDER, RIGHT_SHOULDER)


@dataclass
class PoseKeypoints:
    """Single-frame pose estimation output for one person.

    Attributes:
        xy: (17, 2) array of (x, y) pixel coordinates per keypoint.
        confidence: (17,) array of per-keypoint confidence scores (0.0-1.0).
        timestamp: monotonic time in seconds when the frame was captured.
        person_id: optional tracker ID if multi-person tracking is active.
    """

    xy: np.ndarray  # shape (17, 2)
    confidence: np.ndarray  # shape (17,)
    timestamp: float = 0.0
    person_id: int = 0

    def keypoint(self, idx: int) -> tuple[float, float]:
        """Return (x, y) for a single keypoint."""
        return float(self.xy[idx, 0]), float(self.xy[idx, 1])

    def keypoint_valid(self, idx: int, min_conf: float = 0.3) -> bool:
        """Check if a keypoint has sufficient confidence."""
        return float(self.confidence[idx]) >= min_conf

    def midpoint(self, idx_a: int, idx_b: int) -> tuple[float, float]:
        """Return midpoint between two keypoints."""
        ax, ay = self.keypoint(idx_a)
        bx, by = self.keypoint(idx_b)
        return (ax + bx) / 2.0, (ay + by) / 2.0

    def pelvis_center(self) -> tuple[float, float]:
        """Midpoint of left_hip and right_hip."""
        return self.midpoint(LEFT_HIP, RIGHT_HIP)

    def shoulder_center(self) -> tuple[float, float]:
        """Midpoint of left_shoulder and right_shoulder."""
        return self.midpoint(LEFT_SHOULDER, RIGHT_SHOULDER)

    def torso_center(self) -> tuple[float, float]:
        """Average of all four torso keypoints."""
        pts = [self.keypoint(i) for i in TORSO_KEYPOINTS]
        x = sum(p[0] for p in pts) / len(pts)
        y = sum(p[1] for p in pts) / len(pts)
        return x, y

    def hip_height_normalized(self, frame_height: int) -> float:
        """Pelvis y-position as fraction of frame height (0=top, 1=bottom).

        Lower values mean the person's hips are higher in the frame.
        A value near 1.0 means hips are near the floor.
        """
        _, py = self.pelvis_center()
        return py / frame_height if frame_height > 0 else 0.0

    def torso_angle_degrees(self) -> float:
        """Angle of the torso (shoulder→hip line) relative to vertical.

        0 degrees = perfectly upright (shoulders directly above hips).
        90 degrees = lying flat (shoulders level with hips).
        Uses image coordinates where y increases downward.
        """
        sx, sy = self.shoulder_center()
        px, py = self.pelvis_center()
        dx = sx - px
        dy = sy - py  # negative when shoulders are above hips (upright)
        angle_rad = np.arctan2(abs(dx), abs(dy))
        return float(np.degrees(angle_rad))

    def has_valid_torso(self, min_conf: float = 0.3) -> bool:
        """Check that all four torso keypoints are detected."""
        return all(self.keypoint_valid(i, min_conf) for i in TORSO_KEYPOINTS)
