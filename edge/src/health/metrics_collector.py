import psutil
import time

class MetricsCollector:
    _start_time = time.time()

    def collect(self):
        from src.models.health import SystemMetricsReport
        disk = psutil.disk_usage("/")
        uptime_seconds = int(time.time() - self._start_time)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        return SystemMetricsReport(
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage_percent=disk.percent,
            disk_used_gb=round(disk.used / (1024**3), 1),
            disk_total_gb=round(disk.total / (1024**3), 1),
            edge_device_uptime=f"{days}d {hours}h {minutes}m",
        )
