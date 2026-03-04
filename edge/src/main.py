"""ElderOS Edge Appliance Orchestrator.

Main entry point for the edge device. Supports two operating modes:

  - **simulator**: Generates realistic mock events without hardware sensors,
    useful for backend development, demos, and integration testing.
  - **production**: Runs the full sensor ingestion, inference, processing,
    and publishing pipeline against real cameras, radars, and nurse-call
    hardware.

Usage:
    python -m src.main
    MODE=simulator python -m src.main
    CONFIG_DIR=./config python -m src.main
"""

import asyncio
import logging
import os
import random
import signal
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Subsystem imports
# ---------------------------------------------------------------------------
from src.config import load_config
from src.ingestion.camera_stream import CameraStream
from src.ingestion.radar_reader import RadarReader
from src.ingestion.callbell_listener import CallBellListener
from src.processing.event_processor import EventProcessor
from src.publishing.event_publisher import EventPublisher
from src.health.health_reporter import HealthReporter
from src.health.ntp_sync import NtpSync
from src.storage.clip_manager import ClipManager
from src.storage.clip_server import ClipServer
from src.storage.retention_purger import RetentionPurger
from src.models.events import EdgeEvent, CallBellPayload
from src.models.health import SensorHealthReport, SystemMetricsReport

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("elderos.edge")

# ---------------------------------------------------------------------------
# Shutdown flag shared across coroutines
# ---------------------------------------------------------------------------
_shutdown_event: asyncio.Event | None = None


# ===================================================================
# SIMULATOR MODE
# ===================================================================

# Weighted event distribution that approximates real-world frequency:
#   ~8 bed-exits/day, ~5 inactivity/day, ~3 falls/day, ~1 unsafe-transfer/day
# Total ~17 events/day.  Weights normalised to 1.0:
_EVENT_WEIGHTS = [
    # (event_type, severity, weight)
    ("bed-exit",        "warning",  0.47),   # 8/17
    ("inactivity",      "warning",  0.29),   # 5/17
    ("fall",            "critical", 0.18),   # 3/17
    ("unsafe-transfer", "critical", 0.06),   # 1/17
]

# Confidence ranges per event type  (min%, max%)
_CONFIDENCE_RANGES: dict[str, tuple[int, int]] = {
    "fall":             (60, 95),
    "bed-exit":         (70, 98),
    "inactivity":       (50, 85),
    "unsafe-transfer":  (55, 90),
}

# Call-bell simulation parameters
_CB_ORIGINS = ["room", "bathroom", "hallway"]
_CB_PRIORITIES = ["normal", "urgent", "emergency"]

# Sensor source labels; 10% chance of "fused"
_SENSOR_SOURCES = (["ai-vision"] * 5) + (["ai-sensor"] * 4) + (["fused"] * 1)

# Rooms used by the simulator when sensors.yaml provides no cameras/radars
_FALLBACK_ROOMS: list[tuple[str, str]] = [
    (f"room-{i}", str(i)) for i in range(101, 126)
] + [
    (f"room-{i}", str(i)) for i in range(201, 226)
]


def _pick_weighted_event() -> tuple[str, str]:
    """Return (event_type, severity) using the weighted distribution."""
    roll = random.random()
    cumulative = 0.0
    for event_type, severity, weight in _EVENT_WEIGHTS:
        cumulative += weight
        if roll <= cumulative:
            return event_type, severity
    # Fallback (should not happen due to float rounding)
    return _EVENT_WEIGHTS[0][0], _EVENT_WEIGHTS[0][1]


def _build_rooms_from_config(config) -> list[tuple[str, str]]:
    """Extract (room_id, room_number) pairs from configured sensors."""
    rooms: list[tuple[str, str]] = []
    seen: set[str] = set()
    for cam in config.cameras:
        key = cam.room_id
        if key not in seen:
            rooms.append((cam.room_id, cam.room_number))
            seen.add(key)
    for radar in config.radars:
        key = radar.room_id
        if key not in seen:
            rooms.append((radar.room_id, radar.room_number))
            seen.add(key)
    return rooms if rooms else _FALLBACK_ROOMS


def _unit_for_room(room_number: str) -> str:
    """Derive a unit label from the room number."""
    try:
        num = int(room_number)
        return f"Unit {'A' if num < 200 else 'B'}"
    except ValueError:
        return "Unit A"


def _floor_for_room(room_number: str) -> int:
    """Derive a floor number from the room number."""
    try:
        return 2 if int(room_number) >= 200 else 1
    except ValueError:
        return 1


# --- Simulator coroutines --------------------------------------------------

async def _simulate_detection_events(publisher: EventPublisher, rooms: list[tuple[str, str]]) -> None:
    """Generate mock detection events every 20-40 seconds."""
    logger.info("Simulator: detection event generator started (%d rooms)", len(rooms))
    while not _shutdown_event.is_set():
        delay = random.uniform(20.0, 40.0)
        try:
            await asyncio.wait_for(_shutdown_event.wait(), timeout=delay)
            break  # shutdown signalled
        except asyncio.TimeoutError:
            pass  # normal timeout -- generate an event

        event_type, severity = _pick_weighted_event()
        room_id, room_number = random.choice(rooms)

        conf_min, conf_max = _CONFIDENCE_RANGES[event_type]
        confidence_score = random.randint(conf_min, conf_max)
        if confidence_score >= 85:
            confidence_label = "high"
        elif confidence_score >= 60:
            confidence_label = "medium"
        else:
            confidence_label = "low"

        source = random.choice(_SENSOR_SOURCES)
        is_repeat = (event_type == "fall" and random.random() < 0.15)

        if event_type == "fall":
            post_state = "Simulated: Subject on floor"
        elif event_type == "bed-exit":
            post_state = "Simulated: Subject standing near bed"
        elif event_type == "inactivity":
            post_state = "Simulated: No movement detected"
        else:
            post_state = "Simulated: Unsafe transfer in progress"

        event = EdgeEvent(
            room_id=room_id,
            room_number=room_number,
            resident_id="",
            resident_name="",
            event_type=event_type,
            severity=severity,
            confidence=confidence_label,
            confidence_score=confidence_score,
            sensor_source=source,
            bed_zone=None,
            pre_event_summary="Simulated: Motion detected before event",
            post_event_state=post_state,
            is_repeat_fall=is_repeat,
            detected_at=datetime.now(timezone.utc).isoformat(),
            unit=_unit_for_room(room_number),
        )
        await publisher.publish_event(event)
        logger.info(
            "SIM event: %s in %s (confidence=%d%%, source=%s%s)",
            event_type, room_number, confidence_score, source,
            ", REPEAT" if is_repeat else "",
        )


async def _simulate_callbell_events(publisher: EventPublisher, rooms: list[tuple[str, str]]) -> None:
    """Generate mock call-bell presses every 60-120 seconds."""
    logger.info("Simulator: call-bell event generator started")
    while not _shutdown_event.is_set():
        delay = random.uniform(60.0, 120.0)
        try:
            await asyncio.wait_for(_shutdown_event.wait(), timeout=delay)
            break
        except asyncio.TimeoutError:
            pass

        room_id, room_number = random.choice(rooms)
        origin = random.choice(_CB_ORIGINS)
        priority = random.choice(_CB_PRIORITIES)

        payload = CallBellPayload(
            room_id=room_id,
            room_number=room_number,
            resident_id="",
            resident_name="",
            unit=_unit_for_room(room_number),
            floor=_floor_for_room(room_number),
            origin=origin,
            priority=priority,
            vendor="jeron",
            pressed_at=datetime.now(timezone.utc).isoformat(),
        )
        await publisher.publish_callbell(payload)
        logger.info(
            "SIM call-bell: %s in %s (origin=%s, priority=%s)",
            room_number, room_id, origin, priority,
        )


async def _simulate_sensor_health(publisher: EventPublisher, rooms: list[tuple[str, str]]) -> None:
    """Generate mock sensor health reports every 60 seconds."""
    logger.info("Simulator: sensor health reporter started")
    while not _shutdown_event.is_set():
        try:
            await asyncio.wait_for(_shutdown_event.wait(), timeout=60.0)
            break
        except asyncio.TimeoutError:
            pass

        reports: list[SensorHealthReport] = []
        for room_id, room_number in rooms:
            # Vision sensor
            status = random.choices(["online", "degraded", "offline"], weights=[90, 8, 2], k=1)[0]
            reports.append(SensorHealthReport(
                sensor_id=f"cam-{room_id}",
                type="ai-vision",
                room_id=room_id,
                room_number=room_number,
                status=status,
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
                inference_latency_ms=random.randint(40, 120),
                baseline_latency_ms=80,
                uptime=round(random.uniform(95.0, 100.0), 2),
                firmware_version="v1.2.0-sim",
            ))
            # Radar sensor (50% of rooms have radar)
            if random.random() < 0.5:
                reports.append(SensorHealthReport(
                    sensor_id=f"radar-{room_id}",
                    type="ai-sensor",
                    room_id=room_id,
                    room_number=room_number,
                    status="online",
                    last_heartbeat=datetime.now(timezone.utc).isoformat(),
                    inference_latency_ms=random.randint(10, 50),
                    baseline_latency_ms=30,
                    uptime=round(random.uniform(97.0, 100.0), 2),
                    firmware_version="v2.0.1-sim",
                ))

        await publisher.publish_health(reports)
        logger.debug("SIM health: reported %d sensors", len(reports))


async def _simulate_system_metrics(publisher: EventPublisher) -> None:
    """Generate mock system metrics every 60 seconds."""
    logger.info("Simulator: system metrics reporter started")
    start_time = datetime.now(timezone.utc)
    while not _shutdown_event.is_set():
        try:
            await asyncio.wait_for(_shutdown_event.wait(), timeout=60.0)
            break
        except asyncio.TimeoutError:
            pass

        elapsed = datetime.now(timezone.utc) - start_time
        days = elapsed.days
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60

        metrics = SystemMetricsReport(
            cpu_usage=round(random.uniform(15.0, 65.0), 1),
            memory_usage=round(random.uniform(30.0, 75.0), 1),
            disk_usage_percent=round(random.uniform(20.0, 60.0), 1),
            disk_used_gb=round(random.uniform(10.0, 50.0), 1),
            disk_total_gb=100.0,
            ntp_drift_ms=random.randint(0, 8),
            ntp_sync_status="synced",
            last_self_test_at=datetime.now(timezone.utc).isoformat(),
            self_test_passed=True,
            edge_device_uptime=f"{days}d {hours}h {minutes}m",
        )
        await publisher.publish_metrics(metrics)
        logger.debug("SIM metrics: cpu=%.1f%% mem=%.1f%%", metrics.cpu_usage, metrics.memory_usage)


async def run_simulator(config) -> None:
    """Run the edge appliance in simulator mode.

    Starts the event publisher, then launches concurrent coroutines that
    generate mock detection events, call-bell presses, sensor health
    reports, and system metrics at realistic intervals.
    """
    publisher = EventPublisher(config)
    await publisher.start()

    rooms = _build_rooms_from_config(config)
    logger.info("Simulator using %d rooms", len(rooms))

    tasks = [
        asyncio.create_task(_simulate_detection_events(publisher, rooms), name="sim-detections"),
        asyncio.create_task(_simulate_callbell_events(publisher, rooms), name="sim-callbell"),
        asyncio.create_task(_simulate_sensor_health(publisher, rooms), name="sim-health"),
        asyncio.create_task(_simulate_system_metrics(publisher), name="sim-metrics"),
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Simulator tasks cancelled")
    finally:
        await publisher.stop()
        logger.info("Simulator shutdown complete")


# ===================================================================
# PRODUCTION MODE
# ===================================================================

async def run_production(config) -> None:
    """Run the edge appliance in production mode.

    Starts the full sensor ingestion pipeline (cameras, radars, nurse-call
    listener), inference engines, event processing, health reporting, NTP
    sync, clip storage server, and retention purger.
    """
    # Core services
    publisher = EventPublisher(config)
    await publisher.start()

    processor = EventProcessor(config, publisher)
    health = HealthReporter(config, publisher)
    ntp = NtpSync(config)
    clip_mgr = ClipManager(config)
    clip_srv = ClipServer(config, clip_mgr)
    retention = RetentionPurger(
        clip_mgr.base_path,
        config.clip_storage.retention_days,
        config.clip_storage.purge_threshold_percent,
    )

    tasks: list[asyncio.Task] = []

    # --- Ingestion: cameras ------------------------------------------------
    camera_streams: list[CameraStream] = []
    for cam_cfg in config.cameras:
        stream = CameraStream(cam_cfg, processor)
        camera_streams.append(stream)
        tasks.append(asyncio.create_task(stream.run(), name=f"cam-{cam_cfg.id}"))
    logger.info("Started %d camera stream(s)", len(camera_streams))

    # --- Ingestion: radars -------------------------------------------------
    radar_readers: list[RadarReader] = []
    for radar_cfg in config.radars:
        reader = RadarReader(radar_cfg, processor)
        radar_readers.append(reader)
        tasks.append(asyncio.create_task(reader.run(), name=f"radar-{radar_cfg.id}"))
    logger.info("Started %d radar reader(s)", len(radar_readers))

    # --- Ingestion: call bell ----------------------------------------------
    callbell_listener: CallBellListener | None = None
    if config.callbell:
        callbell_listener = CallBellListener(config.callbell, publisher)
        tasks.append(asyncio.create_task(callbell_listener.run(), name="callbell"))
        logger.info("Started call-bell listener")

    # --- Health & NTP ------------------------------------------------------
    tasks.append(asyncio.create_task(health.run(), name="health"))
    tasks.append(asyncio.create_task(ntp.sync_loop(), name="ntp-sync"))
    logger.info("Started health reporter and NTP sync")

    # --- Clip server (aiohttp on port 8001) --------------------------------
    tasks.append(asyncio.create_task(clip_srv.start(port=8001), name="clip-server"))
    logger.info("Starting clip server on port 8001")

    # --- Retention purger --------------------------------------------------
    async def _retention_loop() -> None:
        while not _shutdown_event.is_set():
            try:
                await retention.purge()
            except Exception as exc:
                logger.error("Retention purge error: %s", exc)
            try:
                await asyncio.wait_for(_shutdown_event.wait(), timeout=3600.0)
                break
            except asyncio.TimeoutError:
                pass

    tasks.append(asyncio.create_task(_retention_loop(), name="retention-purger"))
    logger.info("Started retention purger")

    # --- Wait for shutdown -------------------------------------------------
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Production tasks cancelled")
    finally:
        # Graceful teardown
        for stream in camera_streams:
            stream.stop()
        for reader in radar_readers:
            reader.stop()
        if callbell_listener:
            callbell_listener.stop()
        await publisher.stop()
        logger.info("Production shutdown complete")


# ===================================================================
# SHUTDOWN HANDLING
# ===================================================================

def _request_shutdown() -> None:
    """Signal all coroutines to stop via the shared event, then cancel tasks."""
    logger.info("Shutdown requested -- stopping all tasks")
    if _shutdown_event is not None:
        _shutdown_event.set()

    # Cancel all running tasks except the current one
    loop = asyncio.get_event_loop()
    for task in asyncio.all_tasks(loop):
        if task is not asyncio.current_task():
            task.cancel()


# ===================================================================
# MAIN ENTRY POINT
# ===================================================================

async def main() -> None:
    """Parse config, configure logging, and dispatch to the appropriate mode."""
    global _shutdown_event
    _shutdown_event = asyncio.Event()

    config = load_config(os.environ.get("CONFIG_DIR", "./config"))

    # Reconfigure logging level from config (default INFO)
    log_level_name = "INFO"
    if hasattr(config, "backend") and hasattr(config.backend, "log_level"):
        log_level_name = config.backend.log_level
    log_level_name = os.environ.get("LOG_LEVEL", log_level_name).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.getLogger().setLevel(log_level)

    logger.info("Starting ElderOS Edge in %s mode", config.mode)

    # Register signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _request_shutdown)
        except NotImplementedError:
            # Windows does not support add_signal_handler; fall back to
            # signal.signal which works for SIGINT (Ctrl+C).
            pass

    # On Windows, ensure Ctrl+C still triggers CancelledError
    if sys.platform == "win32":
        def _win_handler(_signum, _frame):
            _request_shutdown()
        signal.signal(signal.SIGINT, _win_handler)
        try:
            signal.signal(signal.SIGTERM, _win_handler)
        except OSError:
            pass  # SIGTERM may not be available on all Windows versions

    try:
        if config.mode == "simulator":
            await run_simulator(config)
        else:
            await run_production(config)
    except asyncio.CancelledError:
        logger.info("Main task cancelled")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("ElderOS Edge stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
