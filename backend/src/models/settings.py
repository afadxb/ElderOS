from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ConfidenceThreshold(Base):
    """Singleton row — id is always 1."""

    __tablename__ = "confidence_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    high_min: Mapped[int] = mapped_column(Integer, default=85)
    medium_min: Mapped[int] = mapped_column(Integer, default=60)
    low_min: Mapped[int] = mapped_column(Integer, default=30)


class RetentionPolicy(Base):
    """Singleton row — id is always 1."""

    __tablename__ = "retention_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    clip_retention_days: Mapped[int] = mapped_column(Integer, default=7)
    metadata_retention_days: Mapped[int] = mapped_column(Integer, default=90)
    auto_purge_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    purge_threshold_percent: Mapped[int] = mapped_column(Integer, default=90)


class ExclusionZone(Base):
    __tablename__ = "exclusion_zones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rooms.id")
    )
    room_number: Mapped[str | None] = mapped_column(String(10))
    zone_name: Mapped[str | None] = mapped_column(String(50))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
