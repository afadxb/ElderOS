import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class CameraStream:
    """Ingests RTSP frames and runs both ONNX and pose-based detection.

    When a PoseEventProcessor is attached, each frame is also passed through
    the pose estimation → rules engine pipeline. Detections from both paths
    are forwarded to the standard EventProcessor for fusion/publishing.
    """

    def __init__(self, camera_config, event_processor, pose_processor=None):
        self.config = camera_config
        self.processor = event_processor
        self.pose_processor = pose_processor  # PoseEventProcessor (optional)
        self.cap = None
        self._running = False

    async def run(self):
        self._running = True
        logger.info("Starting camera stream: %s (room %s)", self.config.id, self.config.room_number)
        while self._running:
            try:
                import cv2
                self.cap = cv2.VideoCapture(self.config.rtsp_url)
                if not self.cap.isOpened():
                    logger.warning("Cannot open RTSP stream: %s", self.config.rtsp_url)
                    await asyncio.sleep(10)
                    continue

                while self._running:
                    ret, frame = await asyncio.to_thread(self.cap.read)
                    if not ret:
                        logger.warning("Lost frame from %s, reconnecting", self.config.id)
                        break

                    timestamp = time.monotonic()

                    # Path 1: ONNX bounding-box detector (existing)
                    detections = await asyncio.to_thread(
                        self.processor.vision_detector.detect, frame
                    )
                    for detection in detections:
                        await self.processor.process_vision_event(
                            self.config.room_id, self.config.room_number, detection
                        )

                    # Path 2: Pose estimation + rules engine (new)
                    if self.pose_processor is not None:
                        pose_detections = await asyncio.to_thread(
                            self.pose_processor.process_frame, frame, timestamp
                        )
                        for detection in pose_detections:
                            await self.processor.process_vision_event(
                                self.config.room_id, self.config.room_number, detection
                            )

                    await asyncio.sleep(0.1)  # ~10 FPS
            except Exception as e:
                logger.error("Camera stream error: %s", e)
            finally:
                if self.cap:
                    self.cap.release()
            await asyncio.sleep(5)  # reconnect delay

    def stop(self):
        self._running = False
