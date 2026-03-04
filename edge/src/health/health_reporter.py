import asyncio
import logging
from datetime import datetime, timezone
from src.health.metrics_collector import MetricsCollector
from src.health.ntp_sync import NtpSync

logger = logging.getLogger(__name__)

class HealthReporter:
    def __init__(self, config, publisher):
        self.config = config
        self.publisher = publisher
        self.metrics_collector = MetricsCollector()
        self.ntp = NtpSync(config)
        self._sensor_statuses: list = []

    def update_sensor_status(self, sensor_id: str, status: str, latency_ms: int):
        """Called by ingestion components to report sensor health."""
        from src.models.health import SensorHealthReport
        for s in self._sensor_statuses:
            if s.sensor_id == sensor_id:
                s.status = status
                s.last_heartbeat = datetime.now(timezone.utc).isoformat()
                s.inference_latency_ms = latency_ms
                return
        # New sensor
        self._sensor_statuses.append(SensorHealthReport(
            sensor_id=sensor_id, type="ai-vision", room_id="", room_number="",
            status=status, last_heartbeat=datetime.now(timezone.utc).isoformat(),
            inference_latency_ms=latency_ms, baseline_latency_ms=80,
            uptime=99.9, firmware_version="v1.0.0"
        ))

    async def run(self):
        # Start NTP sync in background
        asyncio.create_task(self.ntp.sync_loop())
        while True:
            try:
                # Report sensor health
                if self._sensor_statuses:
                    await self.publisher.publish_health(self._sensor_statuses)

                # Report system metrics
                metrics = self.metrics_collector.collect()
                metrics.ntp_drift_ms = self.ntp.current_drift_ms
                metrics.ntp_sync_status = self.ntp.sync_status
                await self.publisher.publish_metrics(metrics)
            except Exception as e:
                logger.error("Health report failed: %s", e)
            await asyncio.sleep(self.config.backend.health_interval_seconds)
