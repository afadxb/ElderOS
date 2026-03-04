"""Re-export sensor configuration dataclasses from config module."""

from src.config import CameraConfig, RadarConfig, CallBellConfig

__all__ = ["CameraConfig", "RadarConfig", "CallBellConfig"]
