from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.room import Room


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rooms.id")
    )
    room_number: Mapped[str | None] = mapped_column(String(10))
    type: Mapped[str | None] = mapped_column(
        String(10), comment="ai-vision|ai-sensor"
    )
    status: Mapped[str] = mapped_column(String(10), default="online")
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime)
    inference_latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    baseline_latency_ms: Mapped[int] = mapped_column(Integer, default=80)
    uptime: Mapped[float] = mapped_column(Float, default=99.9)
    firmware_version: Mapped[str] = mapped_column(
        String(20), default="v1.0.0"
    )

    # Device management columns
    edge_device_id: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    connection_config: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="JSON: rtsp_url, serial_port, etc."
    )
    detection_config: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="JSON: thresholds, sensitivity, etc."
    )

    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="sensors")
