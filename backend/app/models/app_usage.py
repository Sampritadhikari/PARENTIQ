from datetime import date, datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class InstalledApp(Base):
    __tablename__ = "installed_apps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    package_name = Column(String(255), nullable=False)
    app_name = Column(String(255), nullable=False)
    version_name = Column(String(50), nullable=True)
    version_code = Column(Integer, nullable=True)
    category = Column(String(50), default="Other", nullable=False)  # Games, Social, Education, etc.
    is_system_app = Column(Boolean, default=False, nullable=False)
    installed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device = relationship("Device", back_populates="installed_apps")


class AppUsage(Base):
    __tablename__ = "app_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    package_name = Column(String(255), index=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    category = Column(String(50), default="Other", nullable=False)
    usage_date = Column(Date, default=lambda: date.today(), index=True, nullable=False)
    foreground_time_seconds = Column(Integer, default=0, nullable=False)
    launch_count = Column(Integer, default=0, nullable=False)
    last_time_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device = relationship("Device", back_populates="app_usage")


class AppRestriction(Base):
    __tablename__ = "app_restrictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    package_name = Column(String(255), index=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    daily_limit_minutes = Column(Integer, nullable=True)  # Specific limit for this app
    block_during_school = Column(Boolean, default=True, nullable=False)
    block_during_bedtime = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    child = relationship("ChildProfile", back_populates="app_restrictions")

