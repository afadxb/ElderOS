from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sensor import Sensor
from src.models.system_metrics import SystemMetrics
from src.utils.time_utils import dt_to_iso


async def get_sensor_health(db: AsyncSession) -> list[Sensor]:
    """Get all sensors for health monitoring."""
    result = await db.execute(select(Sensor).order_by(Sensor.room_number))
    return list(result.scalars().all())


async def get_latest_metrics(db: AsyncSession) -> SystemMetrics | None:
    """Get the most recent system metrics row."""
    result = await db.execute(
        select(SystemMetrics).order_by(desc(SystemMetrics.recorded_at)).limit(1)
    )
    return result.scalars().first()


async def get_self_test_report(db: AsyncSession) -> dict:
    """Assemble a self-test report from latest metrics and sensor statuses.

    Returns: {"passed": bool, "details": list[str]}
    """
    details: list[str] = []
    all_passed = True

    # Check latest system metrics
    metrics = await get_latest_metrics(db)
    if metrics:
        details.append(
            f"Last self-test at {dt_to_iso(metrics.last_self_test_at)}: "
            f"{'PASSED' if metrics.self_test_passed else 'FAILED'}"
        )
        if not metrics.self_test_passed:
            all_passed = False
        if metrics.cpu_usage and metrics.cpu_usage > 90:
            details.append(f"WARNING: CPU usage at {metrics.cpu_usage}%")
            all_passed = False
        if metrics.memory_usage and metrics.memory_usage > 90:
            details.append(f"WARNING: Memory usage at {metrics.memory_usage}%")
            all_passed = False
        if metrics.disk_usage_percent and metrics.disk_usage_percent > 90:
            details.append(f"WARNING: Disk usage at {metrics.disk_usage_percent}%")
            all_passed = False
        if metrics.ntp_sync_status != "synced":
            details.append(f"WARNING: NTP status is {metrics.ntp_sync_status}")
            all_passed = False
    else:
        details.append("No system metrics available")
        all_passed = False

    # Check sensor statuses
    sensors = await get_sensor_health(db)
    offline_sensors = [s for s in sensors if s.status != "online"]
    details.append(f"Sensors: {len(sensors)} total, {len(offline_sensors)} offline")
    if offline_sensors:
        all_passed = False
        for s in offline_sensors:
            details.append(
                f"  OFFLINE: sensor {s.id} ({s.type}) in room {s.room_number}"
            )

    return {"passed": all_passed, "details": details}


async def upsert_sensor_health(
    db: AsyncSession, sensors_data: list[dict]
) -> None:
    """Update sensor records from edge health reports.

    Each item in sensors_data should have at minimum: sensor_id, status,
    last_heartbeat, inference_latency_ms, uptime.
    """
    for data in sensors_data:
        sensor_id = data.get("sensor_id")
        if not sensor_id:
            continue

        sensor = await db.get(Sensor, sensor_id)
        if not sensor:
            continue

        if "status" in data:
            sensor.status = data["status"]
        if "last_heartbeat" in data:
            # Accept ISO string or datetime
            hb = data["last_heartbeat"]
            if isinstance(hb, str):
                sensor.last_heartbeat = datetime.fromisoformat(hb)
            else:
                sensor.last_heartbeat = hb
        if "inference_latency_ms" in data:
            sensor.inference_latency_ms = data["inference_latency_ms"]
        if "baseline_latency_ms" in data:
            sensor.baseline_latency_ms = data["baseline_latency_ms"]
        if "uptime" in data:
            sensor.uptime = data["uptime"]
        if "firmware_version" in data:
            sensor.firmware_version = data["firmware_version"]

    await db.commit()
