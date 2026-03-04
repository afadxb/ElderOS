"""Rule-based + optional ONNX radar detector for fall/bed-exit/inactivity events.

Processes structured radar data (parsed frames from mmWave or similar sensors).
Falls back to stub mode when no ONNX classifier is available.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from src.inference.base_detector import BaseDetector, Detection

logger = logging.getLogger(__name__)

# Thresholds for rule-based detection
_FALL_HEIGHT_DROP_M = 0.5  # minimum height change in metres
_FALL_VELOCITY_SPIKE_MS = 1.5  # minimum downward velocity m/s
_BED_EXIT_DISTANCE_M = 0.8  # movement distance from bed zone
_INACTIVITY_SECONDS = 300  # 5 minutes without macro movement


@dataclass
class RadarFrame:
    """Parsed radar data for a single time-step.

    Attributes:
        height_m: Estimated target height in metres.
        velocity_ms: Vertical velocity in m/s (negative = downward).
        distance_from_bed_m: Target distance from the bed zone centroid.
        macro_movement: Whether macro-level movement is detected.
        breathing_detected: Whether micro breathing signal is present.
        timestamp: Unix timestamp of the reading.
    """
    height_m: float = 0.0
    velocity_ms: float = 0.0
    distance_from_bed_m: float = 0.0
    macro_movement: bool = True
    breathing_detected: bool = False
    timestamp: float = 0.0


class RadarDetector(BaseDetector):
    """Combines rule-based heuristics with an optional ONNX classifier.

    Rule-based detections:
      - Fall: sudden height drop + velocity spike.
      - Bed exit: presence movement from bed zone to floor.
      - Inactivity: breathing signal present but no macro movement for an
        extended period.

    When an ONNX model is available, its output is fused with the rule-based
    result (classifier confidence replaces the heuristic confidence).
    """

    def __init__(self, config) -> None:
        self._session = None
        self._input_name: str | None = None
        self._stub_mode: bool = True
        self._last_latency_ms: float = 0.0
        self._last_macro_movement: dict[str, float] = {}  # room_id -> timestamp

        model_path = config.inference.radar_model_path
        self.load_model(model_path)

    # --- BaseDetector interface -------------------------------------------

    def load_model(self, model_path: str) -> None:
        path = Path(model_path)
        if not path.exists():
            logger.warning(
                "Radar model not found at %s -- using rule-based detection only",
                model_path,
            )
            self._stub_mode = True
            return

        try:
            import onnxruntime as ort  # type: ignore[import-untyped]

            self._session = ort.InferenceSession(
                str(path), providers=["CPUExecutionProvider"]
            )
            self._input_name = self._session.get_inputs()[0].name
            self._stub_mode = False
            logger.info("Radar classifier loaded from %s", model_path)
        except Exception:
            logger.exception("Failed to load radar ONNX model -- rule-based only")
            self._stub_mode = True

    def detect(self, input_data) -> list[Detection]:
        """Run detection on a RadarFrame (or raw feature vector for ONNX).

        Args:
            input_data: A RadarFrame for rule-based detection, or a numpy
                        array if using the ONNX classifier directly.

        Returns:
            List of Detection objects (usually 0 or 1 per frame).
        """
        if isinstance(input_data, RadarFrame):
            return self._detect_rules(input_data)

        # Numpy array path -- ONNX classifier
        if not self._stub_mode and self._session is not None:
            return self._detect_onnx(input_data)

        return []

    # --- Public helpers ----------------------------------------------------

    @property
    def last_latency_ms(self) -> float:
        return self._last_latency_ms

    @property
    def is_stub(self) -> bool:
        return self._stub_mode

    def update_movement(self, room_id: str, has_macro: bool, timestamp: float) -> None:
        """Track the last time macro movement was observed for a room."""
        if has_macro:
            self._last_macro_movement[room_id] = timestamp

    # --- Rule-based detection ---------------------------------------------

    def _detect_rules(self, frame: RadarFrame) -> list[Detection]:
        detections: list[Detection] = []

        # Fall detection: sudden height drop + velocity spike
        if (
            frame.height_m < _FALL_HEIGHT_DROP_M
            and abs(frame.velocity_ms) >= _FALL_VELOCITY_SPIKE_MS
            and frame.velocity_ms < 0  # downward
        ):
            detections.append(
                Detection(
                    event_type="fall",
                    confidence_score=0.70,
                    metadata={"source": "ai-sensor", "method": "rule-based"},
                )
            )

        # Bed exit: target moved away from bed zone
        if frame.distance_from_bed_m >= _BED_EXIT_DISTANCE_M and frame.macro_movement:
            detections.append(
                Detection(
                    event_type="bed-exit",
                    confidence_score=0.65,
                    metadata={"source": "ai-sensor", "method": "rule-based"},
                )
            )

        # Inactivity: breathing but no macro movement for extended period
        if frame.breathing_detected and not frame.macro_movement:
            # Check how long since last macro movement in this room's context
            room_key = frame.metadata.get("room_id", "_default") if hasattr(frame, "metadata") else "_default"
            last_macro = self._last_macro_movement.get(room_key, frame.timestamp)
            idle_seconds = frame.timestamp - last_macro
            if idle_seconds >= _INACTIVITY_SECONDS:
                detections.append(
                    Detection(
                        event_type="inactivity",
                        confidence_score=0.55,
                        metadata={
                            "source": "ai-sensor",
                            "method": "rule-based",
                            "idle_seconds": idle_seconds,
                        },
                    )
                )

        return detections

    # --- ONNX classifier path ---------------------------------------------

    def _detect_onnx(self, feature_vector) -> list[Detection]:
        import numpy as np

        start = time.monotonic()
        if feature_vector.ndim == 1:
            feature_vector = np.expand_dims(feature_vector, axis=0)
        raw = self._session.run(None, {self._input_name: feature_vector.astype(np.float32)})
        self._last_latency_ms = (time.monotonic() - start) * 1000.0

        detections: list[Detection] = []
        if raw and raw[0] is not None:
            # Expected output: (1, num_classes) probability vector
            probs = raw[0][0]
            class_labels = ["fall", "bed-exit", "inactivity", "unsafe-transfer"]
            best_idx = int(np.argmax(probs))
            best_conf = float(probs[best_idx])
            if best_conf >= 0.30:  # minimum threshold
                detections.append(
                    Detection(
                        event_type=class_labels[best_idx],
                        confidence_score=best_conf,
                        metadata={"source": "ai-sensor", "method": "onnx"},
                    )
                )

        return detections
