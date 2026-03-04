"""Tests for pose-based rules engine, zone geometry, and keypoint tracker."""

import pytest
import numpy as np

from src.models.keypoints import (
    PoseKeypoints,
    LEFT_SHOULDER,
    RIGHT_SHOULDER,
    LEFT_HIP,
    RIGHT_HIP,
    NUM_KEYPOINTS,
)
from src.processing.zone_geometry import BedZone, ZoneManager, point_in_polygon, Point
from src.processing.keypoint_tracker import KeypointTracker, TrackerConfig
from src.processing.pose_rules_engine import PoseRulesEngine, PoseRulesConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pose(
    pelvis_xy: tuple[float, float] = (320, 240),
    shoulder_xy: tuple[float, float] = (320, 140),
    confidence: float = 0.9,
    timestamp: float = 0.0,
) -> PoseKeypoints:
    """Create a PoseKeypoints with controlled torso position.

    Other keypoints are set to reasonable defaults.
    """
    xy = np.zeros((NUM_KEYPOINTS, 2), dtype=np.float32)
    conf = np.full(NUM_KEYPOINTS, confidence, dtype=np.float32)

    # Torso keypoints
    px, py = pelvis_xy
    sx, sy = shoulder_xy
    xy[LEFT_HIP] = [px - 20, py]
    xy[RIGHT_HIP] = [px + 20, py]
    xy[LEFT_SHOULDER] = [sx - 25, sy]
    xy[RIGHT_SHOULDER] = [sx + 25, sy]

    # Fill remaining keypoints with plausible values
    xy[0] = [sx, sy - 30]  # nose
    xy[1] = [sx - 10, sy - 25]  # left eye
    xy[2] = [sx + 10, sy - 25]  # right eye
    xy[3] = [sx - 20, sy - 20]  # left ear
    xy[4] = [sx + 20, sy - 20]  # right ear
    xy[7] = [sx - 40, sy + 40]  # left elbow
    xy[8] = [sx + 40, sy + 40]  # right elbow
    xy[9] = [sx - 50, sy + 80]  # left wrist
    xy[10] = [sx + 50, sy + 80]  # right wrist
    xy[13] = [px - 15, py + 80]  # left knee
    xy[14] = [px + 15, py + 80]  # right knee
    xy[15] = [px - 15, py + 160]  # left ankle
    xy[16] = [px + 15, py + 160]  # right ankle

    return PoseKeypoints(xy=xy, confidence=conf, timestamp=timestamp)


def _make_lying_pose(
    pelvis_xy: tuple[float, float] = (320, 400),
    timestamp: float = 0.0,
) -> PoseKeypoints:
    """Create a pose where the person is lying on the floor.

    Hips are low (high y-value), torso is nearly horizontal.
    """
    px, py = pelvis_xy
    # Shoulders at the same height as hips = lying flat
    return _make_pose(
        pelvis_xy=(px, py),
        shoulder_xy=(px + 100, py + 5),  # shoulders ~level with hips
        timestamp=timestamp,
    )


def _make_bed_zone() -> BedZone:
    """Bed zone covering the left half of the frame."""
    return BedZone(
        room_id="room-101",
        vertices=[
            (0.05, 0.20),
            (0.50, 0.20),
            (0.50, 0.90),
            (0.05, 0.90),
        ],
    )


# ---------------------------------------------------------------------------
# Zone Geometry Tests
# ---------------------------------------------------------------------------


class TestPointInPolygon:
    def test_point_inside_rectangle(self):
        poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
        assert point_in_polygon(Point(0.5, 0.5), poly) is True

    def test_point_outside_rectangle(self):
        poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
        assert point_in_polygon(Point(1.5, 0.5), poly) is False

    def test_point_on_edge(self):
        poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
        # Edge behavior is implementation-defined; just ensure no crash
        result = point_in_polygon(Point(0.5, 0.0), poly)
        assert isinstance(result, bool)

    def test_triangle(self):
        poly = [Point(0, 0), Point(1, 0), Point(0.5, 1)]
        assert point_in_polygon(Point(0.5, 0.3), poly) is True
        assert point_in_polygon(Point(0.9, 0.9), poly) is False

    def test_degenerate_polygon(self):
        assert point_in_polygon(Point(0, 0), [Point(0, 0), Point(1, 0)]) is False


class TestBedZone:
    def test_contains_normalized(self):
        zone = _make_bed_zone()
        assert zone.contains_normalized(0.25, 0.50) is True
        assert zone.contains_normalized(0.75, 0.50) is False

    def test_contains_pixel(self):
        zone = _make_bed_zone()
        # 640x480 frame: pixel (160, 240) = normalized (0.25, 0.50) -> inside
        assert zone.contains_pixel(160, 240, 640, 480) is True
        # pixel (480, 240) = normalized (0.75, 0.50) -> outside
        assert zone.contains_pixel(480, 240, 640, 480) is False

    def test_zero_dimensions(self):
        zone = _make_bed_zone()
        assert zone.contains_pixel(100, 100, 0, 0) is False


class TestZoneManager:
    def test_from_config(self):
        cameras = [
            {
                "room_id": "room-101",
                "bed_zone": {
                    "vertices": [[0.1, 0.2], [0.5, 0.2], [0.5, 0.8], [0.1, 0.8]],
                    "label": "bed",
                },
            },
            {"room_id": "room-102"},  # No bed zone
        ]
        manager = ZoneManager.from_config(cameras)
        assert manager.has_zone("room-101")
        assert not manager.has_zone("room-102")

    def test_get_zone(self):
        manager = ZoneManager()
        zone = _make_bed_zone()
        manager.add_zone(zone)
        assert manager.get_zone("room-101") is zone
        assert manager.get_zone("room-999") is None


# ---------------------------------------------------------------------------
# Keypoint Tracker Tests
# ---------------------------------------------------------------------------


class TestKeypointTracker:
    def test_smoothing_first_frame(self):
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=0.5))
        pose = _make_pose(timestamp=0.0)
        smoothed = tracker.update(pose)
        # First frame should be identical
        np.testing.assert_array_almost_equal(smoothed.xy, pose.xy)

    def test_smoothing_reduces_jitter(self):
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=0.3))

        # Frame 1: stable position
        pose1 = _make_pose(pelvis_xy=(320, 240), timestamp=0.0)
        tracker.update(pose1)

        # Frame 2: jittery jump
        pose2 = _make_pose(pelvis_xy=(340, 260), timestamp=0.1)
        smoothed = tracker.update(pose2)

        # Smoothed pelvis should be between original and jittery position
        px, py = smoothed.pelvis_center()
        assert 320 < px < 340
        assert 240 < py < 260

    def test_history_window(self):
        tracker = KeypointTracker(config=TrackerConfig(window_seconds=1.0))
        for i in range(20):
            pose = _make_pose(timestamp=float(i) * 0.1)
            tracker.update(pose)

        history = tracker.get_history()
        # Should only keep ~1 second worth (10 frames at 0.1s intervals)
        assert len(history) <= 11

    def test_hip_height_velocity(self):
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))  # No smoothing

        # Person standing (hips at y=240 in 480-height frame = 0.5)
        pose1 = _make_pose(pelvis_xy=(320, 240), timestamp=0.0)
        tracker.update(pose1)

        # Person fallen (hips at y=400 in 480-height frame = 0.83)
        pose2 = _make_pose(pelvis_xy=(320, 400), timestamp=0.5)
        tracker.update(pose2)

        velocity = tracker.hip_height_velocity(frame_height=480, interval_seconds=0.5)
        assert velocity is not None
        # (0.83 - 0.5) / 0.5 = 0.66/s -> positive = downward
        assert velocity > 0.5

    def test_get_latest(self):
        tracker = KeypointTracker()
        assert tracker.get_latest() is None
        pose = _make_pose(timestamp=1.0)
        tracker.update(pose)
        assert tracker.get_latest() is not None
        assert tracker.get_latest().timestamp == 1.0


# ---------------------------------------------------------------------------
# PoseKeypoints Model Tests
# ---------------------------------------------------------------------------


class TestPoseKeypoints:
    def test_pelvis_center(self):
        pose = _make_pose(pelvis_xy=(300, 200))
        px, py = pose.pelvis_center()
        assert abs(px - 300) < 1
        assert abs(py - 200) < 1

    def test_torso_angle_upright(self):
        # Shoulders directly above hips
        pose = _make_pose(pelvis_xy=(320, 300), shoulder_xy=(320, 150))
        angle = pose.torso_angle_degrees()
        assert angle < 10  # Near vertical

    def test_torso_angle_lying(self):
        # Shoulders level with hips (lying flat)
        pose = _make_pose(pelvis_xy=(320, 300), shoulder_xy=(450, 300))
        angle = pose.torso_angle_degrees()
        assert angle > 80  # Near horizontal

    def test_hip_height_normalized(self):
        pose = _make_pose(pelvis_xy=(320, 360))
        h = pose.hip_height_normalized(480)
        assert abs(h - 0.75) < 0.05

    def test_has_valid_torso(self):
        pose = _make_pose(confidence=0.9)
        assert pose.has_valid_torso(min_conf=0.3) is True

        low_conf_pose = _make_pose(confidence=0.1)
        assert low_conf_pose.has_valid_torso(min_conf=0.3) is False


# ---------------------------------------------------------------------------
# Pose Rules Engine Tests
# ---------------------------------------------------------------------------


class TestBedExitRule:
    def _make_engine(self) -> tuple[PoseRulesEngine, PoseRulesConfig]:
        cfg = PoseRulesConfig(
            bed_exit_confirm_frames=3,
            bed_exit_upright_max_angle=45.0,
            bed_exit_cooldown_seconds=5.0,
            frame_height=480,
            frame_width=640,
        )
        zone = _make_bed_zone()
        engine = PoseRulesEngine(bed_zone=zone, config=cfg)
        return engine, cfg

    def test_no_event_when_in_bed(self):
        engine, _ = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        # Person in bed zone, upright
        for i in range(10):
            pose = _make_pose(pelvis_xy=(160, 300), timestamp=float(i) * 0.1)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            assert len(detections) == 0

    def test_bed_exit_fires_after_confirm_frames(self):
        engine, cfg = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        # First: establish person is in bed
        for i in range(3):
            pose = _make_pose(pelvis_xy=(160, 300), timestamp=float(i) * 0.1)
            tracker.update(pose)
            engine.evaluate(tracker)

        # Then: person exits bed (pelvis at x=480 = normalized 0.75, outside zone)
        fired = False
        for i in range(3, 3 + cfg.bed_exit_confirm_frames + 2):
            pose = _make_pose(
                pelvis_xy=(480, 240),
                shoulder_xy=(480, 140),  # upright
                timestamp=float(i) * 0.1,
            )
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            if detections:
                fired = True
                assert detections[0].event_type == "bed-exit"
                assert detections[0].metadata["rule"] == "bed-exit"
                break

        assert fired, "Bed-exit should have fired"

    def test_no_fire_when_not_upright(self):
        engine, cfg = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        # In bed first
        for i in range(3):
            pose = _make_pose(pelvis_xy=(160, 300), timestamp=float(i) * 0.1)
            tracker.update(pose)
            engine.evaluate(tracker)

        # Exit bed but lying down (not upright)
        for i in range(3, 20):
            pose = _make_lying_pose(pelvis_xy=(480, 300), timestamp=float(i) * 0.1)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            bed_exit_events = [d for d in detections if d.event_type == "bed-exit"]
            assert len(bed_exit_events) == 0

    def test_cooldown_prevents_rapid_refire(self):
        engine, cfg = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        # In bed
        for i in range(3):
            pose = _make_pose(pelvis_xy=(160, 300), timestamp=float(i) * 0.1)
            tracker.update(pose)
            engine.evaluate(tracker)

        # Exit bed → fires
        t = 0.3
        for _ in range(cfg.bed_exit_confirm_frames + 2):
            pose = _make_pose(pelvis_xy=(480, 240), timestamp=t)
            tracker.update(pose)
            engine.evaluate(tracker)
            t += 0.1

        # Back in bed briefly, then exit again — should NOT fire (cooldown)
        for _ in range(3):
            pose = _make_pose(pelvis_xy=(160, 300), timestamp=t)
            tracker.update(pose)
            engine.evaluate(tracker)
            t += 0.1

        for _ in range(cfg.bed_exit_confirm_frames + 2):
            pose = _make_pose(pelvis_xy=(480, 240), timestamp=t)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            bed_exit_events = [d for d in detections if d.event_type == "bed-exit"]
            assert len(bed_exit_events) == 0, "Should be in cooldown"
            t += 0.1


class TestOnFloorRule:
    def _make_engine(self) -> tuple[PoseRulesEngine, PoseRulesConfig]:
        cfg = PoseRulesConfig(
            on_floor_hip_threshold=0.75,
            on_floor_lying_min_angle=55.0,
            on_floor_sustain_seconds=1.0,
            on_floor_cooldown_seconds=5.0,
            frame_height=480,
            frame_width=640,
        )
        engine = PoseRulesEngine(bed_zone=None, config=cfg)
        return engine, cfg

    def test_on_floor_fires_after_sustain(self):
        engine, cfg = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        fired = False
        for i in range(20):
            t = float(i) * 0.1  # 0.1s per frame
            pose = _make_lying_pose(pelvis_xy=(320, 400), timestamp=t)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            on_floor = [d for d in detections if d.event_type == "on-floor"]
            if on_floor:
                fired = True
                assert on_floor[0].metadata["rule"] == "on-floor"
                assert t >= cfg.on_floor_sustain_seconds
                break

        assert fired, "On-floor should have fired after sustain period"

    def test_no_fire_when_standing(self):
        engine, _ = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        for i in range(30):
            pose = _make_pose(
                pelvis_xy=(320, 240),
                shoulder_xy=(320, 140),
                timestamp=float(i) * 0.1,
            )
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            on_floor = [d for d in detections if d.event_type == "on-floor"]
            assert len(on_floor) == 0

    def test_resets_when_person_stands(self):
        engine, _ = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        # Lying for 0.5s (not enough to trigger)
        for i in range(5):
            pose = _make_lying_pose(pelvis_xy=(320, 400), timestamp=float(i) * 0.1)
            tracker.update(pose)
            engine.evaluate(tracker)

        # Stand up — resets timer
        for i in range(5, 10):
            pose = _make_pose(
                pelvis_xy=(320, 240), shoulder_xy=(320, 140),
                timestamp=float(i) * 0.1,
            )
            tracker.update(pose)
            engine.evaluate(tracker)

        # Lie down again for 0.5s — still shouldn't fire (timer reset)
        for i in range(10, 15):
            pose = _make_lying_pose(pelvis_xy=(320, 400), timestamp=float(i) * 0.1)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            on_floor = [d for d in detections if d.event_type == "on-floor"]
            assert len(on_floor) == 0


class TestFallSuspectedRule:
    def _make_engine(self) -> tuple[PoseRulesEngine, PoseRulesConfig]:
        cfg = PoseRulesConfig(
            fall_hip_velocity_threshold=0.5,
            fall_velocity_window=0.5,
            fall_confirm_window_seconds=2.0,
            fall_cooldown_seconds=5.0,
            on_floor_hip_threshold=0.75,
            on_floor_lying_min_angle=55.0,
            frame_height=480,
            frame_width=640,
        )
        engine = PoseRulesEngine(bed_zone=None, config=cfg)
        return engine, cfg

    def test_fall_detected(self):
        engine, _ = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0, window_seconds=5.0))

        # Standing for a few frames
        for i in range(5):
            pose = _make_pose(
                pelvis_xy=(320, 200), shoulder_xy=(320, 100),
                timestamp=float(i) * 0.1,
            )
            tracker.update(pose)
            engine.evaluate(tracker)

        # Rapid drop: hips go from y=200 to y=400 in 0.5s
        t = 0.5
        for i in range(5):
            y = 200 + (i + 1) * 40  # 240, 280, 320, 360, 400
            pose = _make_lying_pose(pelvis_xy=(320, y), timestamp=t)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            fall_events = [d for d in detections if d.event_type == "fall"]
            if fall_events:
                assert fall_events[0].metadata["rule"] == "fall-suspected"
                return  # Test passes
            t += 0.1

        # Give a few more frames on the floor to confirm
        for i in range(10):
            pose = _make_lying_pose(pelvis_xy=(320, 400), timestamp=t)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            fall_events = [d for d in detections if d.event_type == "fall"]
            if fall_events:
                assert fall_events[0].metadata["rule"] == "fall-suspected"
                return
            t += 0.1

        pytest.fail("Fall-suspected should have fired")

    def test_no_fall_on_slow_descent(self):
        engine, _ = self._make_engine()
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0, window_seconds=5.0))

        # Very slow descent (sitting down slowly)
        t = 0.0
        for i in range(50):
            y = 200 + i * 4  # slow: 4px per 0.1s = 8.3% of frame per second
            if y > 400:
                y = 400
            pose = _make_pose(
                pelvis_xy=(320, y),
                shoulder_xy=(320, y - 100),
                timestamp=t,
            )
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            fall_events = [d for d in detections if d.event_type == "fall"]
            assert len(fall_events) == 0, f"Should not detect fall on slow movement at t={t}"
            t += 0.1


class TestNoZoneGraceful:
    """Rules engine should work gracefully without a bed zone."""

    def test_bed_exit_skipped_without_zone(self):
        engine = PoseRulesEngine(bed_zone=None, config=PoseRulesConfig())
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        for i in range(20):
            pose = _make_pose(pelvis_xy=(480, 240), timestamp=float(i) * 0.1)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            bed_exit = [d for d in detections if d.event_type == "bed-exit"]
            assert len(bed_exit) == 0

    def test_on_floor_works_without_zone(self):
        cfg = PoseRulesConfig(
            on_floor_sustain_seconds=0.5,
            on_floor_cooldown_seconds=1.0,
            frame_height=480,
        )
        engine = PoseRulesEngine(bed_zone=None, config=cfg)
        tracker = KeypointTracker(config=TrackerConfig(ema_alpha=1.0))

        fired = False
        for i in range(20):
            pose = _make_lying_pose(pelvis_xy=(320, 400), timestamp=float(i) * 0.1)
            tracker.update(pose)
            detections = engine.evaluate(tracker)
            if any(d.event_type == "on-floor" for d in detections):
                fired = True
                break
        assert fired
