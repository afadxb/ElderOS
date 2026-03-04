from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.resident import Resident
    from src.models.sensor import Sensor


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    number: Mapped[str] = mapped_column(String(10), nullable=False)
    unit_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("units.id"), nullable=True
    )
    unit_name: Mapped[str | None] = mapped_column(String(50))
    floor: Mapped[int | None] = mapped_column(Integer)
    room_type: Mapped[str | None] = mapped_column(
        String(15), comment="single|semi-private"
    )
    sensor_type: Mapped[str | None] = mapped_column(
        String(10), comment="ai-vision|ai-sensor|hybrid"
    )
    status: Mapped[str] = mapped_column(String(15), default="clear")
    status_color: Mapped[str] = mapped_column(String(10), default="green")
    has_exclusion_zone: Mapped[bool] = mapped_column(Boolean, default=False)
    bed_zone_vertices: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="JSON array of [x,y] normalized vertices"
    )
    last_event_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now()
    )

    # Relationships
    residents: Mapped[List["Resident"]] = relationship(
        "Resident", back_populates="room"
    )
    sensors: Mapped[List["Sensor"]] = relationship(
        "Sensor", back_populates="room"
    )
