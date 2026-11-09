from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    device_name = Column(String(100), nullable=False)
    device_model = Column(String(100), nullable=True)
    os_version = Column(String(50), nullable=True)  # e.g., Android 14
    app_version = Column(String(50), nullable=True)
    device_fingerprint = Column(String(255), unique=True, index=True, nullable=False)
    fcm_token = Column(String(512), nullable=True)
    is_online = Column(Boolean, default=False, nullable=False)
    battery_level = Column(Integer, default=100, nullable=False)
    is_charging = Column(Boolean, default=False, nullable=False)
    network_type = Column(String(50), default="unknown", nullable=False)  # wifi, cellular, none
    last_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    child = relationship("ChildProfile", back_populates="devices")
    permissions = relationship("DevicePermission", back_populates="device", uselist=False, cascade="all, delete-orphan")
    location_history = relationship("LocationHistory", back_populates="device", cascade="all, delete-orphan")
    app_usage = relationship("AppUsage", back_populates="device", cascade="all, delete-orphan")
    installed_apps = relationship("InstalledApp", back_populates="device", cascade="all, delete-orphan")
    screen_time_logs = relationship("ScreenTimeLog", back_populates="device", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="device", cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="device", cascade="all, delete-orphan")

