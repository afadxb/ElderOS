"""Core event processing pipeline.

Receives raw detections from vision and radar sensors, applies fusion,
scoring, exclusion filtering, and repeat detection, then publishes
finalised EdgeEvent objects via the configured publisher.
"""

from datetime import datetime, timezone

from src.inference.base_detector import Detection
from src.inference.vision_detector import VisionDetector
from src.inference.radar_detector import RadarDetector
from src.models.events import EdgeEvent
from src.processing.sensor_fusion import SensorFusion
from src.processing.confidence_scorer import ConfidenceScorer
from src.processing.exclusion_filter import ExclusionFilter
from src.processing.repeat_detector import RepeatDetector


class EventProcessor:
    """Orchestrates the detection-to-event pipeline for a single edge device."""

    def __init__(self, config, publisher) -> None:
        self.config = config
        self.fusion = SensorFusion(config)
        self.scorer = ConfidenceScorer(config)
        self.exclusion = ExclusionFilter(config)
        self.repeat = RepeatDetector()
        self.publisher = publisher
        self.vision_detector = VisionDetector(config.inference.vision_model_path)
        self.radar_detector = RadarDetector(config)

    # --- Public entry points -----------------------------------------------

    async def process_vision_event(
        self, room_id: str, room_number: str, detection: Detection
    ) -> None:
        """Process a detection originating from a camera (vision) sensor."""
        if self.exclusion.is_excluded(room_id, detection):
            return

        fused = self.fusion.try_fuse(room_id, "vision", detection)
        scored = self.scorer.score(detection, source="ai-vision", fused=fused)
        is_repeat = self.repeat.check(room_id, detection.event_type)
        event = self._build_event(room_id, room_number, scored, fused, is_repeat)
        await self.publisher.publish_event(event)

    async def process_radar_event(
        self, room_id: str, room_number: str, detection: Detection
    ) -> None:
        """Process a detection originating from a radar sensor."""
        if self.exclusion.is_excluded(room_id, detection):
            return

        fused = self.fusion.try_fuse(room_id, "radar", detection)
        scored = self.scorer.score(detection, source="ai-sensor", fused=fused)
        is_repeat = self.repeat.check(room_id, detection.event_type)
        event = self._build_event(room_id, room_number, scored, fused, is_repeat)
        await self.publisher.publish_event(event)

    # --- Event construction ------------------------------------------------

    @staticmethod
    def _build_event(
        room_id: str,
        room_number: str,
        scored: Detection,
        fused: bool,
        is_repeat: bool,
    ) -> EdgeEvent:
        """Construct an EdgeEvent from a scored detection."""
        severity = (
            "critical"
            if scored.event_type in ("fall", "unsafe-transfer")
            else "warning"
        )

        if scored.confidence_score >= 0.85:
            confidence_label = "high"
        elif scored.confidence_score >= 0.60:
            confidence_label = "medium"
        else:
            confidence_label = "low"

        sensor_source: str
        if fused:
            sensor_source = "fused"
        else:
            sensor_source = scored.metadata.get("source", "ai-vision")

        return EdgeEvent(
            room_id=room_id,
            room_number=room_number,
            resident_id="",  # Edge may not know resident identity
            resident_name="",
            event_type=scored.event_type,
            severity=severity,
            confidence=confidence_label,
            confidence_score=int(scored.confidence_score * 100),
            sensor_source=sensor_source,
            bed_zone=None,
            pre_event_summary="Motion detected before event",
            post_event_state="Monitoring post-event",
            is_repeat_fall=is_repeat,
            detected_at=datetime.now(timezone.utc).isoformat(),
        )
