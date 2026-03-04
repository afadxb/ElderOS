"""ONNX-based vision detector for fall/event detection from camera frames.

Gracefully degrades to a no-op stub when the ONNX model file is missing
or ONNX Runtime is unavailable (simulator mode).
"""

import logging
import time
from pathlib import Path

import numpy as np

from src.inference.base_detector import BaseDetector, Detection

logger = logging.getLogger(__name__)

# Event type labels indexed by model output class id
_EVENT_LABELS: dict[int, str] = {
    0: "fall",
    1: "bed-exit",
    2: "inactivity",
    3: "unsafe-transfer",
}

# Expected model input dimensions
_INPUT_WIDTH = 640
_INPUT_HEIGHT = 640


class VisionDetector(BaseDetector):
    """Runs ONNX vision inference on camera frames.

    If the model file does not exist or onnxruntime cannot be imported the
    detector operates in stub mode and returns an empty detection list.
    Inference latency is tracked for health reporting.
    """

    def __init__(self, model_path: str) -> None:
        self._session = None
        self._input_name: str | None = None
        self._stub_mode: bool = True
        self._last_latency_ms: float = 0.0
        self.load_model(model_path)

    # --- BaseDetector interface -------------------------------------------

    def load_model(self, model_path: str) -> None:
        """Load the ONNX model if available, otherwise activate stub mode."""
        path = Path(model_path)
        if not path.exists():
            logger.warning(
                "Vision model not found at %s -- running in stub mode", model_path
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
            logger.info("Vision model loaded from %s", model_path)
        except Exception:
            logger.exception("Failed to load vision ONNX model -- falling back to stub")
            self._stub_mode = True

    def detect(self, input_data: np.ndarray) -> list[Detection]:
        """Run inference on a single BGR camera frame.

        Args:
            input_data: numpy array of shape (H, W, 3) in BGR colour order.

        Returns:
            List of Detection objects for events found in the frame.
        """
        if self._stub_mode or self._session is None:
            return []

        blob = self._preprocess(input_data)

        start = time.monotonic()
        raw_output = self._session.run(None, {self._input_name: blob})
        elapsed = time.monotonic() - start
        self._last_latency_ms = elapsed * 1000.0

        return self._postprocess(raw_output)

    # --- Public helpers ----------------------------------------------------

    @property
    def last_latency_ms(self) -> float:
        """Inference latency of the most recent detect() call in milliseconds."""
        return self._last_latency_ms

    @property
    def is_stub(self) -> bool:
        return self._stub_mode

    # --- Internal ----------------------------------------------------------

    @staticmethod
    def _preprocess(frame: np.ndarray) -> np.ndarray:
        """Resize + normalise a BGR frame into the model's expected input tensor."""
        import cv2  # type: ignore[import-untyped]

        resized = cv2.resize(frame, (_INPUT_WIDTH, _INPUT_HEIGHT))
        # HWC -> CHW, BGR -> RGB, normalise to 0-1
        blob = resized[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        # Add batch dimension -> (1, 3, H, W)
        return np.expand_dims(blob, axis=0)

    @staticmethod
    def _postprocess(raw_output: list) -> list[Detection]:
        """Convert raw ONNX output tensor into Detection objects.

        Expected output shape: (1, N, 6) where each row is
        [x, y, w, h, confidence, class_id].
        Adjust this method to match your specific model's output format.
        """
        detections: list[Detection] = []
        if not raw_output or raw_output[0] is None:
            return detections

        predictions = raw_output[0]
        # Handle both (1, N, 6) and (N, 6) shapes
        if predictions.ndim == 3:
            predictions = predictions[0]

        for row in predictions:
            if len(row) < 6:
                continue
            x, y, w, h = int(row[0]), int(row[1]), int(row[2]), int(row[3])
            confidence = float(row[4])
            class_id = int(row[5])

            event_type = _EVENT_LABELS.get(class_id)
            if event_type is None:
                continue

            detections.append(
                Detection(
                    event_type=event_type,
                    confidence_score=confidence,
                    bounding_box=(x, y, w, h),
                    metadata={"class_id": class_id},
                )
            )

        return detections
