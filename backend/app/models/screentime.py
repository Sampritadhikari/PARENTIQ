from datetime import date, datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ScreenTimeRule(Base):
    __tablename__ = "screen_time_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    daily_limit_minutes = Column(Integer, default=120, nullable=False)  # 2 hours default
    school_mode_enabled = Column(Boolean, default=False, nullable=False)
    school_mode_start = Column(String(10), default="08:30", nullable=True)  # HH:MM
    school_mode_end = Column(String(10), default="15:30", nullable=True)
    school_mode_days = Column(JSON, default=lambda: [1, 2, 3, 4, 5], nullable=False)  # Mon-Fri
    bedtime_mode_enabled = Column(Boolean, default=False, nullable=False)
    bedtime_start = Column(String(10), default="21:00", nullable=True)  # HH:MM
    bedtime_end = Column(String(10), default="07:00", nullable=True)
    bedtime_days = Column(JSON, default=lambda: [0, 1, 2, 3, 4, 5, 6], nullable=False)
    instant_lock = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    child = relationship("ChildProfile", back_populates="screen_time_rules")


class ScreenTimeLog(Base):
    __tablename__ = "screen_time_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    log_date = Column(Date, default=lambda: date.today(), index=True, nullable=False)
    total_screen_time_seconds = Column(Integer, default=0, nullable=False)
    unlock_count = Column(Integer, default=0, nullable=False)
    extra_time_granted_minutes = Column(Integer, default=0, nullable=False)
    bonus_requests_pending = Column(Integer, default=0, nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device = relationship("Device", back_populates="screen_time_logs")

