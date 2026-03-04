"""Pose-based rules engine for Bed-Exit, On-Floor, and Fall-Suspected events.

Evaluates smoothed keypoint data against configurable thresholds to produce
Detection objects compatible with the existing EventProcessor pipeline.

Rules:
    Bed-Exit:  Pelvis leaves bed-zone + upright posture sustained for N frames.
    On-Floor:  Hip height near floor + lying angle sustained for N seconds.
    Fall-Suspected: Rapid hip height drop + transition to On-Floor state.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

from src.inference.base_detector import Detection
from src.models.keypoints import PoseKeypoints
from src.processing.keypoint_tracker import KeypointTracker
from src.processing.zone_geometry import BedZone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class PoseRulesConfig:
    """Tunable thresholds for all three pose rules."""

    # --- Bed-Exit ---
    # Number of consecutive frames with pelvis outside bed-zone + upright
    bed_exit_confirm_frames: int = 6
    # Max torso angle (degrees) to be considered "upright" (0=vertical, 90=flat)
    bed_exit_upright_max_angle: float = 45.0
    # Minimum confidence score on the generated Detection
    bed_exit_min_confidence: float = 0.85
    # Cooldown in seconds before the same event can fire again
    bed_exit_cooldown_seconds: float = 30.0

    # --- On-Floor ---
    # Hip height as fraction of frame height above which = "on floor"
    on_floor_hip_threshold: float = 0.75
    # Minimum torso angle (degrees) to be considered "lying" (near 90=flat)
    on_floor_lying_min_angle: float = 55.0
    # How many seconds the on-floor state must persist before firing
    on_floor_sustain_seconds: float = 3.0
    on_floor_min_confidence: float = 0.85
    on_floor_cooldown_seconds: float = 60.0

    # --- Fall-Suspected ---
    # Minimum hip-height velocity (normalized units/sec) to count as a fall
    # Positive = downward movement in image coords
    fall_hip_velocity_threshold: float = 0.8
    # Time window (seconds) over which to measure hip velocity
    fall_velocity_window: float = 0.5
    # After detecting rapid drop, require on-floor state within this window
    fall_confirm_window_seconds: float = 2.0
    fall_min_confidence: float = 0.80
    fall_cooldown_seconds: float = 60.0

    # --- General ---
    frame_height: int = 480  # Default frame height for normalized calculations
    frame_width: int = 640
    min_keypoint_confidence: float = 0.3


# ---------------------------------------------------------------------------
# Internal state per room
# ---------------------------------------------------------------------------

class _PersonState(Enum):
    UNKNOWN = "unknown"
    IN_BED = "in_bed"
    OUT_OF_BED = "out_of_bed"
    ON_FLOOR = "on_floor"


@dataclass
class _RoomRuleState:
    """Mutable per-room state for rule evaluation."""

    # Bed-Exit tracking
    person_state: _PersonState = _PersonState.UNKNOWN
    frames_outside_bed_upright: int = 0
    last_bed_exit_time: float = field(default=float("-inf"))

    # On-Floor tracking
    floor_state_start: float | None = None  # When the on-floor condition first met
    last_on_floor_time: float = field(default=float("-inf"))

    # Fall-Suspected tracking
    rapid_drop_detected_at: float | None = None
    last_fall_time: float = field(default=float("-inf"))


# ---------------------------------------------------------------------------
# Rules Engine
# ---------------------------------------------------------------------------

class PoseRulesEngine:
    """Evaluates per-frame pose data against rules for a single room.

    Usage:
        engine = PoseRulesEngine(bed_zone=zone, config=config)
        detections = engine.evaluate(tracker)
        # detections is a list[Detection] compatible with EventProcessor

    Call evaluate() once per frame after updating the KeypointTracker.
    """

    def __init__(
        self,
        bed_zone: BedZone | None = None,
        config: PoseRulesConfig | None = None,
    ) -> None:
        self.bed_zone = bed_zone
        self.config = config or PoseRulesConfig()
        self._state = _RoomRuleState()

    def evaluate(self, tracker: KeypointTracker) -> list[Detection]:
        """Run all rules against current tracker state.

        Args:
            tracker: KeypointTracker with up-to-date smoothed pose data.

        Returns:
            List of Detection objects for any events that fired this frame.
        """
        pose = tracker.get_latest()
        if pose is None or not pose.has_valid_torso(self.config.min_keypoint_confidence):
            # No valid pose — reset transient counters but don't clear state
            self._state.frames_outside_bed_upright = 0
            return []

        detections: list[Detection] = []
        now = pose.timestamp

        bed_exit = self._eval_bed_exit(pose, now)
        if bed_exit:
            detections.append(bed_exit)

        on_floor = self._eval_on_floor(pose, now)
        if on_floor:
            detections.append(on_floor)

        fall = self._eval_fall_suspected(pose, tracker, now)
        if fall:
            detections.append(fall)

        return detections

    def reset(self) -> None:
        """Clear all rule state (e.g., when a room goes offline)."""
        self._state = _RoomRuleState()

    # --- Individual Rules --------------------------------------------------

    def _eval_bed_exit(self, pose: PoseKeypoints, now: float) -> Detection | None:
        """Bed-Exit: pelvis outside bed-zone + upright posture for N frames."""
        cfg = self.config

        # Cooldown check
        if now - self._state.last_bed_exit_time < cfg.bed_exit_cooldown_seconds:
            return None

        # Need a bed zone to evaluate this rule
        if self.bed_zone is None:
            return None

        px, py = pose.pelvis_center()
        in_bed = self.bed_zone.contains_pixel(
            px, py, cfg.frame_width, cfg.frame_height
        )
        torso_angle = pose.torso_angle_degrees()
        is_upright = torso_angle < cfg.bed_exit_upright_max_angle

        if in_bed:
            # Person is in bed — track state, reset counter
            self._state.person_state = _PersonState.IN_BED
            self._state.frames_outside_bed_upright = 0
            return None

        if is_upright:
            self._state.frames_outside_bed_upright += 1
        else:
            self._state.frames_outside_bed_upright = 0

        if self._state.frames_outside_bed_upright < cfg.bed_exit_confirm_frames:
            return None

        # Only fire if person was previously known to be in bed
        if self._state.person_state != _PersonState.IN_BED:
            self._state.person_state = _PersonState.OUT_OF_BED
            return None

        # Fire bed-exit event
        self._state.person_state = _PersonState.OUT_OF_BED
        self._state.frames_outside_bed_upright = 0
        self._state.last_bed_exit_time = now
        logger.info("Bed-Exit detected (room zone: %s)", self.bed_zone.room_id)

        return Detection(
            event_type="bed-exit",
            confidence_score=cfg.bed_exit_min_confidence,
            bounding_box=None,
            metadata={
                "source": "pose-rules",
                "rule": "bed-exit",
                "torso_angle": round(torso_angle, 1),
                "pelvis_xy": [round(px, 1), round(py, 1)],
            },
        )

    def _eval_on_floor(self, pose: PoseKeypoints, now: float) -> Detection | None:
        """On-Floor: hip height near floor + lying angle for N seconds."""
        cfg = self.config

        # Cooldown check
        if now - self._state.last_on_floor_time < cfg.on_floor_cooldown_seconds:
            return None

        hip_h = pose.hip_height_normalized(cfg.frame_height)
        torso_angle = pose.torso_angle_degrees()

        hips_low = hip_h >= cfg.on_floor_hip_threshold
        is_lying = torso_angle >= cfg.on_floor_lying_min_angle

        if hips_low and is_lying:
            if self._state.floor_state_start is None:
                self._state.floor_state_start = now

            elapsed = now - self._state.floor_state_start
            if elapsed >= cfg.on_floor_sustain_seconds:
                # Fire on-floor event
                self._state.person_state = _PersonState.ON_FLOOR
                self._state.floor_state_start = None
                self._state.last_on_floor_time = now
                logger.info(
                    "On-Floor detected (hip_h=%.2f, angle=%.1f, sustained=%.1fs)",
                    hip_h, torso_angle, elapsed,
                )
                return Detection(
                    event_type="on-floor",
                    confidence_score=cfg.on_floor_min_confidence,
                    bounding_box=None,
                    metadata={
                        "source": "pose-rules",
                        "rule": "on-floor",
                        "hip_height_norm": round(hip_h, 3),
                        "torso_angle": round(torso_angle, 1),
                        "sustained_seconds": round(elapsed, 1),
                    },
                )
        else:
            # Condition not met — reset timer
            self._state.floor_state_start = None
            if self._state.person_state == _PersonState.ON_FLOOR:
                # Person recovered from floor
                self._state.person_state = _PersonState.UNKNOWN

        return None

    def _eval_fall_suspected(
        self, pose: PoseKeypoints, tracker: KeypointTracker, now: float
    ) -> Detection | None:
        """Fall-Suspected: rapid hip drop + transition to on-floor state."""
        cfg = self.config

        # Cooldown check
        if now - self._state.last_fall_time < cfg.fall_cooldown_seconds:
            return None

        velocity = tracker.hip_height_velocity(
            cfg.frame_height, interval_seconds=cfg.fall_velocity_window
        )

        if velocity is None:
            return None

        # Phase 1: detect rapid downward movement
        if velocity >= cfg.fall_hip_velocity_threshold:
            if self._state.rapid_drop_detected_at is None:
                self._state.rapid_drop_detected_at = now
                logger.debug("Rapid hip drop detected (v=%.2f/s)", velocity)

        # Phase 2: within confirm window, check if person is now on floor
        if self._state.rapid_drop_detected_at is not None:
            elapsed = now - self._state.rapid_drop_detected_at

            if elapsed > cfg.fall_confirm_window_seconds:
                # Window expired without floor confirmation — reset
                self._state.rapid_drop_detected_at = None
                return None

            hip_h = pose.hip_height_normalized(cfg.frame_height)
            torso_angle = pose.torso_angle_degrees()
            hips_low = hip_h >= cfg.on_floor_hip_threshold
            is_lying = torso_angle >= cfg.on_floor_lying_min_angle

            if hips_low and is_lying:
                # Confirmed: rapid drop + now on floor = fall suspected
                self._state.rapid_drop_detected_at = None
                self._state.last_fall_time = now
                self._state.person_state = _PersonState.ON_FLOOR
                logger.info(
                    "Fall-Suspected (velocity=%.2f/s, hip_h=%.2f, angle=%.1f)",
                    velocity, hip_h, torso_angle,
                )
                return Detection(
                    event_type="fall",
                    confidence_score=cfg.fall_min_confidence,
                    bounding_box=None,
                    metadata={
                        "source": "pose-rules",
                        "rule": "fall-suspected",
                        "hip_velocity": round(velocity, 2),
                        "hip_height_norm": round(hip_h, 3),
                        "torso_angle": round(torso_angle, 1),
                    },
                )

        return None
