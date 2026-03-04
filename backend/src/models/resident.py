from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.room import Room


class Resident(Base):
    __tablename__ = "residents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    room_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("rooms.id"), nullable=True
    )
    room_number: Mapped[str | None] = mapped_column(String(10))
    unit: Mapped[str | None] = mapped_column(String(50))
    bed_zone: Mapped[str | None] = mapped_column(
        String(1), nullable=True, comment="A|B|null"
    )
    age: Mapped[int | None] = mapped_column(Integer)
    risk_score: Mapped[int] = mapped_column(Integer, default=50)
    risk_trend: Mapped[str] = mapped_column(String(10), default="stable")
    fall_count_30d: Mapped[int] = mapped_column(Integer, default=0)
    fall_count_total: Mapped[int] = mapped_column(Integer, default=0)
    last_fall_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    last_event_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    admitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    observe_only: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now()
    )

    # Relationships
    room: Mapped["Room | None"] = relationship("Room", back_populates="residents")
