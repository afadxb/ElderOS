"""YAML configuration loader for the ElderOS edge appliance."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class BackendConfig:
    url: str = "http://backend:8000"
    api_key: str = "edge-device-shared-secret"
    health_interval_seconds: int = 60
    metrics_interval_seconds: int = 60
    retry_max_attempts: int = 5
    retry_base_delay_seconds: int = 2


@dataclass
class InferenceConfig:
    vision_model_path: str = "./models/fall_detection.onnx"
    radar_model_path: str = "./models/radar_classifier.onnx"
    confidence_thresholds: dict = field(
        default_factory=lambda: {"high_min": 85, "medium_min": 60, "low_min": 30}
    )
    processing_fps: int = 10


@dataclass
class FusionConfig:
    time_window_seconds: int = 5
    confidence_boost: int = 15


@dataclass
class ClipStorageConfig:
    base_path: str = "/data/clips"
    pre_event_seconds: int = 10
    post_event_seconds: int = 15
    retention_days: int = 7
    purge_threshold_percent: int = 90


@dataclass
class NtpConfig:
    server: str = "pool.ntp.org"
    sync_interval_seconds: int = 300
    drift_warn_ms: int = 10
    drift_critical_ms: int = 50


@dataclass
class SelfTestConfig:
    schedule_hour: int = 3


@dataclass
class CameraConfig:
    id: str
    rtsp_url: str
    room_id: str
    room_number: str
    type: str = "ai-vision"
    bed_zone: dict | None = None


@dataclass
class RadarConfig:
    id: str
    serial_port: str
    baud_rate: int
    room_id: str
    room_number: str
    type: str = "ai-sensor"


@dataclass
class CallBellConfig:
    vendor: str = "jeron"
    host: str = "192.168.1.200"
    port: int = 4000
    protocol: str = "tcp"


@dataclass
class EdgeConfig:
    backend: BackendConfig = field(default_factory=BackendConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    clip_storage: ClipStorageConfig = field(default_factory=ClipStorageConfig)
    ntp: NtpConfig = field(default_factory=NtpConfig)
    self_test: SelfTestConfig = field(default_factory=SelfTestConfig)
    cameras: list[CameraConfig] = field(default_factory=list)
    radars: list[RadarConfig] = field(default_factory=list)
    callbell: CallBellConfig | None = None
    edge_device_id: str = "edge-default"
    config_sync_interval_seconds: int = 120
    mode: str = "simulator"


def _build_backend(data: dict) -> BackendConfig:
    """Build BackendConfig from YAML dict with env var overrides."""
    return BackendConfig(
        url=os.environ.get("BACKEND_URL", data.get("url", "http://backend:8000")),
        api_key=os.environ.get(
            "BACKEND_API_KEY", data.get("api_key", "edge-device-shared-secret")
        ),
        health_interval_seconds=int(
            os.environ.get(
                "BACKEND_HEALTH_INTERVAL",
                data.get("health_interval_seconds", 60),
            )
        ),
        metrics_interval_seconds=int(
            os.environ.get(
                "BACKEND_METRICS_INTERVAL",
                data.get("metrics_interval_seconds", 60),
            )
        ),
        retry_max_attempts=int(
            os.environ.get(
                "BACKEND_RETRY_MAX", data.get("retry_max_attempts", 5)
            )
        ),
        retry_base_delay_seconds=int(
            os.environ.get(
                "BACKEND_RETRY_DELAY", data.get("retry_base_delay_seconds", 2)
            )
        ),
    )


def _build_inference(data: dict) -> InferenceConfig:
    """Build InferenceConfig from YAML dict with env var overrides."""
    return InferenceConfig(
        vision_model_path=os.environ.get(
            "VISION_MODEL_PATH", data.get("vision_model_path", "./models/fall_detection.onnx")
        ),
        radar_model_path=os.environ.get(
            "RADAR_MODEL_PATH", data.get("radar_model_path", "./models/radar_classifier.onnx")
        ),
        confidence_thresholds=data.get(
            "confidence_thresholds", {"high_min": 85, "medium_min": 60, "low_min": 30}
        ),
        processing_fps=int(
            os.environ.get("PROCESSING_FPS", data.get("processing_fps", 10))
        ),
    )


def _build_fusion(data: dict) -> FusionConfig:
    """Build FusionConfig from YAML dict."""
    return FusionConfig(
        time_window_seconds=int(data.get("time_window_seconds", 5)),
        confidence_boost=int(data.get("confidence_boost", 15)),
    )


def _build_clip_storage(data: dict) -> ClipStorageConfig:
    """Build ClipStorageConfig from YAML dict with env var overrides."""
    return ClipStorageConfig(
        base_path=os.environ.get("CLIP_BASE_PATH", data.get("base_path", "/data/clips")),
        pre_event_seconds=int(data.get("pre_event_seconds", 10)),
        post_event_seconds=int(data.get("post_event_seconds", 15)),
        retention_days=int(data.get("retention_days", 7)),
        purge_threshold_percent=int(data.get("purge_threshold_percent", 90)),
    )


def _build_ntp(data: dict) -> NtpConfig:
    """Build NtpConfig from YAML dict."""
    return NtpConfig(
        server=data.get("server", "pool.ntp.org"),
        sync_interval_seconds=int(data.get("sync_interval_seconds", 300)),
        drift_warn_ms=int(data.get("drift_warn_ms", 10)),
        drift_critical_ms=int(data.get("drift_critical_ms", 50)),
    )


def _build_self_test(data: dict) -> SelfTestConfig:
    """Build SelfTestConfig from YAML dict."""
    return SelfTestConfig(
        schedule_hour=int(data.get("schedule_hour", 3)),
    )


def load_config(config_dir: str = "./config") -> EdgeConfig:
    """Load config from YAML files, with env var overrides.

    Reads default.yaml for application settings and sensors.yaml for
    sensor-to-room mappings.  Environment variables take priority over
    YAML values for key settings (BACKEND_URL, BACKEND_API_KEY, MODE, etc.).
    """
    config_path = Path(config_dir)

    # Load default.yaml
    default_data: dict = {}
    default_file = config_path / "default.yaml"
    if default_file.exists():
        with open(default_file) as f:
            default_data = yaml.safe_load(f) or {}

    # Load sensors.yaml
    sensors_data: dict = {}
    sensors_file = config_path / "sensors.yaml"
    if sensors_file.exists():
        with open(sensors_file) as f:
            sensors_data = yaml.safe_load(f) or {}

    # Build sub-configs
    backend = _build_backend(default_data.get("backend", {}))
    inference = _build_inference(default_data.get("inference", {}))
    fusion = _build_fusion(default_data.get("fusion", {}))
    clip_storage = _build_clip_storage(default_data.get("clip_storage", {}))
    ntp = _build_ntp(default_data.get("ntp", {}))
    self_test = _build_self_test(default_data.get("self_test", {}))

    # Edge device identity
    edge_device_id = os.environ.get(
        "EDGE_DEVICE_ID", default_data.get("edge_device_id", "edge-default")
    )
    config_sync_interval_seconds = int(
        default_data.get("config_sync_interval_seconds", 120)
    )

    # Mode — env var overrides YAML
    mode = os.environ.get("MODE", default_data.get("mode", "simulator"))

    # Build sensor configs from sensors.yaml
    cameras = [CameraConfig(**cam) for cam in sensors_data.get("cameras", [])]
    radars = [RadarConfig(**radar) for radar in sensors_data.get("radars", [])]

    callbell_data = sensors_data.get("callbell")
    callbell = CallBellConfig(**callbell_data) if callbell_data else None

    return EdgeConfig(
        backend=backend,
        inference=inference,
        fusion=fusion,
        clip_storage=clip_storage,
        ntp=ntp,
        self_test=self_test,
        cameras=cameras,
        radars=radars,
        callbell=callbell,
        edge_device_id=edge_device_id,
        config_sync_interval_seconds=config_sync_interval_seconds,
        mode=mode,
    )
