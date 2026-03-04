"""Tests for the sensor fusion module."""

import pytest
from unittest.mock import MagicMock

from src.inference.base_detector import Detection
from src.processing.sensor_fusion import SensorFusion


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(window: int = 5, boost: int = 15):
    config = MagicMock()
    config.fusion.time_window_seconds = window
    config.fusion.confidence_boost = boost
    return config


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_no_fusion_single_source():
    """A single detection from one source should not be marked as fused."""
    fusion = SensorFusion(_make_config())
    detection = Detection(event_type="fall", confidence_score=0.80, metadata={})

    result = fusion.try_fuse("room-1", "vision", detection)

    assert result is False


def test_fusion_two_sources_same_room():
    """Two detections from different sources for the same room and event type
    within the time window should be fused."""
    fusion = SensorFusion(_make_config(window=10))

    det_vision = Detection(event_type="fall", confidence_score=0.80, metadata={})
    det_radar = Detection(event_type="fall", confidence_score=0.75, metadata={})

    first = fusion.try_fuse("room-1", "vision", det_vision)
    assert first is False  # No complementary detection yet

    second = fusion.try_fuse("room-1", "radar", det_radar)
    assert second is True  # Fused with the pending vision detection


def test_no_fusion_different_event_types():
    """Two detections of different event types should not fuse."""
    fusion = SensorFusion(_make_config())

    det_fall = Detection(event_type="fall", confidence_score=0.80, metadata={})
    det_bed = Detection(event_type="bed-exit", confidence_score=0.75, metadata={})

    fusion.try_fuse("room-1", "vision", det_fall)
    result = fusion.try_fuse("room-1", "radar", det_bed)

    assert result is False


def test_no_fusion_different_rooms():
    """Detections from different rooms should not fuse."""
    fusion = SensorFusion(_make_config())

    det1 = Detection(event_type="fall", confidence_score=0.80, metadata={})
    det2 = Detection(event_type="fall", confidence_score=0.75, metadata={})

    fusion.try_fuse("room-1", "vision", det1)
    result = fusion.try_fuse("room-2", "radar", det2)

    assert result is False
