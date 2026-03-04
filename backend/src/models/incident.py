from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.escalation import EscalationStep


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), unique=True
    )
    room_number: Mapped[str | None] = mapped_column(String(10))
    resident_name: Mapped[str | None] = mapped_column(String(100))
    resident_id: Mapped[str | None] = mapped_column(String(36))
    event_type: Mapped[str | None] = mapped_column(String(20))
    confidence: Mapped[str | None] = mapped_column(String(10))
    confidence_score: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(15))
    ntp_timestamp: Mapped[str | None] = mapped_column(String(50))
    detected_at: Mapped[datetime | None] = mapped_column(DateTime)
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ack_response_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    resolve_response_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    acknowledged_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    pre_event_summary: Mapped[str | None] = mapped_column(Text)
    post_event_state: Mapped[str | None] = mapped_column(Text)
    is_repeat_fall: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    unit: Mapped[str | None] = mapped_column(String(50))
    sensor_source: Mapped[str | None] = mapped_column(String(10))
    bed_zone: Mapped[str | None] = mapped_column(String(1), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now()
    )

    # Relationships
    escalation_steps: Mapped[List["EscalationStep"]] = relationship(
        "EscalationStep",
        back_populates="incident",
        order_by="EscalationStep.triggered_at",
    )
