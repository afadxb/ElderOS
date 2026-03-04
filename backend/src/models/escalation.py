from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.incident import Incident


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    delay_minutes: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(
        String(10), comment="sms|page|call|email"
    )
    target: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class EscalationStep(Base):
    __tablename__ = "escalation_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id")
    )
    level: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(200))
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    incident: Mapped["Incident"] = relationship(
        "Incident", back_populates="escalation_steps"
    )
