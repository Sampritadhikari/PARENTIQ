from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class DevicePairing(Base):
    __tablename__ = "device_pairings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    pairing_code = Column(String(10), index=True, nullable=False)  # 6-digit code e.g. "492817"
    device_token = Column(String(255), unique=True, index=True, nullable=False)  # Token returned once paired
    is_used = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    paired_device_id = Column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class DevicePermission(Base):
    __tablename__ = "device_permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), unique=True, nullable=False)
    has_location_permission = Column(Boolean, default=False, nullable=False)
    has_background_location = Column(Boolean, default=False, nullable=False)
    has_usage_stats = Column(Boolean, default=False, nullable=False)
    has_accessibility = Column(Boolean, default=False, nullable=False)
    has_notification_listener = Column(Boolean, default=False, nullable=False)
    has_overlay_permission = Column(Boolean, default=False, nullable=False)
    has_battery_optimization_ignored = Column(Boolean, default=False, nullable=False)
    has_media_projection = Column(Boolean, default=False, nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device = relationship("Device", back_populates="permissions")

