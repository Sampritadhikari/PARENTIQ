from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ParentProfile(Base):
    __tablename__ = "parent_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    pin_hash = Column(String(255), nullable=True)  # For sensitive approvals/modes
    fcm_token = Column(String(512), nullable=True)
    notification_preferences = Column(JSON, default=lambda: {
        "location_alerts": True,
        "geofence_alerts": True,
        "screentime_alerts": True,
        "app_install_alerts": True,
        "safety_keyword_alerts": True,
        "battery_alerts": True,
        "device_offline_alerts": True,
    }, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="parent_profile")
    children = relationship("ChildProfile", back_populates="parent", cascade="all, delete-orphan")

