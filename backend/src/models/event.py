from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_status", "status"),
        Index("ix_events_room_id_status", "room_id", "status"),
        Index("ix_events_detected_at_desc", "detected_at", postgresql_using="btree"),
        Index(
            "ix_events_resident_id_detected_at_desc",
            "resident_id",
            "detected_at",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rooms.id"), nullable=False
    )
    room_number: Mapped[str | None] = mapped_column(String(10))
    resident_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("residents.id"), nullable=True
    )
    resident_name: Mapped[str | None] = mapped_column(String(100))
    event_type: Mapped[str] = mapped_column(
        String(20), comment="fall|bed-exit|inactivity|unsafe-transfer"
    )
    severity: Mapped[str | None] = mapped_column(String(10))
    confidence: Mapped[str | None] = mapped_column(
        String(10), comment="high|medium|low"
    )
    confidence_score: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(15), comment="active|acknowledged|resolved|dismissed|escalated"
    )
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    acknowledged_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    pre_event_summary: Mapped[str | None] = mapped_column(Text)
    post_event_state: Mapped[str | None] = mapped_column(Text)
    is_repeat_fall: Mapped[bool] = mapped_column(Boolean, default=False)
    unit: Mapped[str | None] = mapped_column(String(50))
    sensor_source: Mapped[str | None] = mapped_column(
        String(10), comment="ai-vision|ai-sensor|fused"
    )
    bed_zone: Mapped[str | None] = mapped_column(String(1), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now()
    )
