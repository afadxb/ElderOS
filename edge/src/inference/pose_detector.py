"""Pose estimation detector for TRT-Pose / BodyPoseNet on Jetson.

Outputs PoseKeypoints (17 COCO keypoints per person) from camera frames.
Gracefully degrades to stub mode when the model or TensorRT is unavailable,
allowing rule engine development and testing without hardware.
"""

import logging
import time
from pathlib import Path

import numpy as np

from src.models.keypoints import PoseKeypoints, NUM_KEYPOINTS

logger = logging.getLogger(__name__)

_INPUT_WIDTH = 224
_INPUT_HEIGHT = 224


class PoseDetector:
    """Runs pose estimation inference on camera frames.

    In production (Jetson), uses TRT-Pose with TensorRT backend.
    Falls back to ONNX Runtime on x86, or stub mode if no model is available.
    """

    def __init__(self, model_path: str) -> None:
        self._session = None
        self._stub_mode: bool = True
        self._last_latency_ms: float = 0.0
        self._backend: str = "stub"
        self.load_model(model_path)

    def load_model(self, model_path: str) -> None:
        path = Path(model_path)
        if not path.exists():
            logger.warning(
                "Pose model not found at %s -- running in stub mode", model_path
            )
            self._stub_mode = True
            return

        # Try TensorRT first (Jetson), then ONNX Runtime (dev machine)
        if path.suffix == ".engine":
            self._load_tensorrt(path)
        else:
            self._load_onnx(path)

    def detect(self, frame: np.ndarray, timestamp: float = 0.0) -> list[PoseKeypoints]:
        """Run pose estimation on a single BGR camera frame.

        Args:
            frame: numpy array of shape (H, W, 3) in BGR colour order.
            timestamp: monotonic time in seconds for this frame.

        Returns:
            List of PoseKeypoints, one per detected person.
        """
        if self._stub_mode:
            return []

        start = time.monotonic()
        raw = self._infer(frame)
        self._last_latency_ms = (time.monotonic() - start) * 1000.0

        return self._postprocess(raw, timestamp)

    @property
    def last_latency_ms(self) -> float:
        return self._last_latency_ms

    @property
    def is_stub(self) -> bool:
        return self._stub_mode

    @property
    def backend(self) -> str:
        return self._backend

    # --- Backend loaders ---------------------------------------------------

    def _load_tensorrt(self, path: Path) -> None:
        """Load a TensorRT serialised engine (Jetson deployment)."""
        try:
            import tensorrt  # noqa: F401
            # TensorRT loading will be implemented when Jetson hardware arrives.
            # For now, fall through to stub mode.
            logger.info("TensorRT engine found at %s (loader pending)", path)
            self._stub_mode = True
            self._backend = "tensorrt-pending"
        except ImportError:
            logger.warning("TensorRT not available -- stub mode")
            self._stub_mode = True

    def _load_onnx(self, path: Path) -> None:
        """Load an ONNX model via ONNX Runtime."""
        try:
            import onnxruntime as ort

            self._session = ort.InferenceSession(
                str(path), providers=["CPUExecutionProvider"]
            )
            self._input_name = self._session.get_inputs()[0].name
            self._stub_mode = False
            self._backend = "onnxruntime"
            logger.info("Pose model loaded from %s (ONNX Runtime)", path)
        except Exception:
            logger.exception("Failed to load pose ONNX model -- stub mode")
            self._stub_mode = True

    # --- Inference ---------------------------------------------------------

    def _infer(self, frame: np.ndarray) -> list:
        """Run raw model inference. Returns model-specific output."""
        if self._session is None:
            return []

        import cv2

        resized = cv2.resize(frame, (_INPUT_WIDTH, _INPUT_HEIGHT))
        blob = resized[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        blob = np.expand_dims(blob, axis=0)

        return self._session.run(None, {self._input_name: blob})

    def _postprocess(
        self, raw_output: list, timestamp: float
    ) -> list[PoseKeypoints]:
        """Convert model output to PoseKeypoints.

        Expected TRT-Pose output: counts tensor + peaks tensor.
        Adjust this method to match the actual model output format.
        """
        if not raw_output:
            return []

        results: list[PoseKeypoints] = []

        # Generic handler: assumes output[0] is (N_persons, 17, 3)
        # where last dim is (x_norm, y_norm, confidence).
        # Adapt when the actual model format is confirmed on hardware.
        predictions = raw_output[0]
        if predictions.ndim == 3 and predictions.shape[1] == NUM_KEYPOINTS:
            for person_idx in range(predictions.shape[0]):
                person = predictions[person_idx]  # (17, 3)
                xy = person[:, :2].copy()
                conf = person[:, 2].copy()

                # Skip persons with very few valid keypoints
                if np.sum(conf > 0.1) < 4:
                    continue

                results.append(
                    PoseKeypoints(
                        xy=xy,
                        confidence=conf,
                        timestamp=timestamp,
                        person_id=person_idx,
                    )
                )

        return results
