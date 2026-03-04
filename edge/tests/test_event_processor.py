"""Tests for the edge event processing pipeline."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from src.inference.base_detector import Detection
from src.models.events import EdgeEvent
from src.processing.event_processor import EventProcessor

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config():
    """Build a minimal config stub for EventProcessor."""
    config = MagicMock()
    config.fusion.time_window_seconds = 5
    config.fusion.confidence_boost = 15
    config.inference.confidence_thresholds = {"high_min": 85, "medium_min": 60, "low_min": 30}
    config.inference.vision_model_path = "fake_model.onnx"
    return config


def _make_processor(publisher=None):
    """Create an EventProcessor with mocked dependencies.

    The vision and radar detectors are heavy (ONNX loading), so we patch
    the entire processor and only test the pipeline orchestration.
    """
    config = _make_config()
    if publisher is None:
        publisher = AsyncMock()

    processor = object.__new__(EventProcessor)
    processor.config = config

    # Manually wire lightweight components
    from src.processing.sensor_fusion import SensorFusion
    from src.processing.confidence_scorer import ConfidenceScorer
    from src.processing.exclusion_filter import ExclusionFilter
    from src.processing.repeat_detector import RepeatDetector

    processor.fusion = SensorFusion(config)
    processor.scorer = ConfidenceScorer(config)
    processor.exclusion = ExclusionFilter(config)
    processor.repeat = RepeatDetector()
    processor.publisher = publisher
    processor.vision_detector = MagicMock()
    processor.radar_detector = MagicMock()

    return processor


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_process_detection_builds_event():
    """A mock detection processed through process_vision_event produces a
    published EdgeEvent with the expected fields."""
    publisher = AsyncMock()
    processor = _make_processor(publisher)

    detection = Detection(
        event_type="fall",
        confidence_score=0.90,
        bounding_box=(100, 200, 50, 80),
        metadata={},
    )

    await processor.process_vision_event("room-1", "101", detection)

    publisher.publish_event.assert_awaited_once()
    event: EdgeEvent = publisher.publish_event.call_args[0][0]
    assert isinstance(event, EdgeEvent)
    assert event.room_id == "room-1"
    assert event.room_number == "101"
    assert event.event_type == "fall"
    assert event.severity == "critical"
    assert event.confidence == "high"
    assert event.confidence_score >= 85  # 0.90 * 100
    assert event.sensor_source == "ai-vision"


async def test_exclusion_filter_passes():
    """A detection in a non-excluded zone passes through the pipeline and gets
    published."""
    publisher = AsyncMock()
    processor = _make_processor(publisher)

    detection = Detection(
        event_type="bed-exit",
        confidence_score=0.70,
        metadata={},
    )

    # Exclusion filter uses a stub that never excludes
    await processor.process_vision_event("room-2", "102", detection)

    publisher.publish_event.assert_awaited_once()
    event: EdgeEvent = publisher.publish_event.call_args[0][0]
    assert event.event_type == "bed-exit"
    assert event.severity == "warning"
