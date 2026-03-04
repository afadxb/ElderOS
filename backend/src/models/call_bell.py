from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CallBellEvent(Base):
    __tablename__ = "call_bell_events"
    __table_args__ = (
        Index("ix_call_bell_events_status", "status"),
        Index("ix_call_bell_events_pressed_at_desc", "pressed_at"),
        Index("ix_call_bell_events_unit_pressed_at_desc", "unit", "pressed_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rooms.id")
    )
    room_number: Mapped[str | None] = mapped_column(String(10))
    resident_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    resident_name: Mapped[str | None] = mapped_column(String(100))
    unit: Mapped[str | None] = mapped_column(String(50))
    floor: Mapped[int | None] = mapped_column(Integer)
    origin: Mapped[str | None] = mapped_column(
        String(10), comment="bedside|bathroom|hallway|pendant"
    )
    priority: Mapped[str | None] = mapped_column(
        String(10), comment="emergency|urgent|normal"
    )
    status: Mapped[str] = mapped_column(String(10), default="active")
    vendor: Mapped[str | None] = mapped_column(
        String(10), comment="jeron|rauland|hill-rom"
    )
    pressed_at: Mapped[datetime | None] = mapped_column(DateTime)
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    response_time_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    responded_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    responded_by_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    shift: Mapped[str | None] = mapped_column(String(10))
