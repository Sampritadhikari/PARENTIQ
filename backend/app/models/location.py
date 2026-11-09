from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class LocationHistory(Base):
    __tablename__ = "location_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # in meters
    speed = Column(Float, nullable=True)  # in m/s
    altitude = Column(Float, nullable=True)  # in meters
    battery_level = Column(Integer, nullable=True)
    provider = Column(String(50), default="gps", nullable=False)  # gps, network, fused
    address = Column(String(512), nullable=True)
    recorded_at = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    device = relationship("Device", back_populates="location_history")


class Geofence(Base):
    __tablename__ = "geofences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Home", "Lincoln High School"
    zone_type = Column(String(50), default="safe", nullable=False)  # safe, dangerous, restricted
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, default=200.0, nullable=False)  # radius in meters
    notify_on_entry = Column(Boolean, default=True, nullable=False)
    notify_on_exit = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    child = relationship("ChildProfile", back_populates="geofences")

