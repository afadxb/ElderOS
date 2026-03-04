from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cpu_usage: Mapped[float | None] = mapped_column(Float)
    memory_usage: Mapped[float | None] = mapped_column(Float)
    disk_usage_percent: Mapped[float | None] = mapped_column(Float)
    disk_used_gb: Mapped[float | None] = mapped_column(Float)
    disk_total_gb: Mapped[float | None] = mapped_column(Float)
    retention_days: Mapped[int] = mapped_column(Integer, default=7)
    auto_purge_threshold_percent: Mapped[int] = mapped_column(
        Integer, default=90
    )
    ntp_drift_ms: Mapped[int] = mapped_column(Integer, default=0)
    ntp_sync_status: Mapped[str] = mapped_column(
        String(10), default="synced"
    )
    last_self_test_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    self_test_passed: Mapped[bool] = mapped_column(Boolean, default=True)
    edge_device_uptime: Mapped[str] = mapped_column(
        String(30), default="0d 0h 0m"
    )
    recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now()
    )
