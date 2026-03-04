import asyncio
import logging
import struct

logger = logging.getLogger(__name__)

class RadarReader:
    MAGIC_WORD = b'\x02\x01\x04\x03\x06\x05\x08\x07'

    def __init__(self, radar_config, event_processor):
        self.config = radar_config
        self.processor = event_processor
        self._running = False

    async def run(self):
        self._running = True
        logger.info("Starting radar reader: %s (room %s)", self.config.id, self.config.room_number)
        while self._running:
            try:
                import serial_asyncio
                reader, writer = await serial_asyncio.open_serial_connection(
                    url=self.config.serial_port, baudrate=self.config.baud_rate
                )
                buffer = b""
                while self._running:
                    data = await reader.read(4096)
                    if not data:
                        break
                    buffer += data
                    frames = self._extract_frames(buffer)
                    for frame_data, remaining in frames:
                        buffer = remaining
                        parsed = self._parse_radar_frame(frame_data)
                        if parsed:
                            detections = self.processor.radar_detector.detect(parsed)
                            for detection in detections:
                                await self.processor.process_radar_event(
                                    self.config.room_id, self.config.room_number, detection
                                )
            except ImportError:
                logger.warning("pyserial-asyncio not installed, radar reader disabled")
                return
            except Exception as e:
                logger.error("Radar reader error: %s", e)
            await asyncio.sleep(5)

    def _extract_frames(self, buffer: bytes) -> list[tuple[bytes, bytes]]:
        """Extract complete radar frames from buffer."""
        frames = []
        while True:
            idx = buffer.find(self.MAGIC_WORD)
            if idx == -1:
                break
            if len(buffer) < idx + 40:  # Need at least header
                break
            # Parse header to get total packet length
            header = buffer[idx:idx + 40]
            try:
                total_length = struct.unpack('<I', header[12:16])[0]
            except struct.error:
                buffer = buffer[idx + 8:]
                continue
            if len(buffer) < idx + total_length:
                break
            frame = buffer[idx:idx + total_length]
            buffer = buffer[idx + total_length:]
            frames.append((frame, buffer))
        return frames

    def _parse_radar_frame(self, frame: bytes) -> dict | None:
        """Parse TI mmWave radar frame into structured data."""
        try:
            return {
                "raw": frame,
                "timestamp": asyncio.get_event_loop().time(),
                "point_count": len(frame) // 16,  # Simplified
            }
        except Exception:
            return None

    def stop(self):
        self._running = False
