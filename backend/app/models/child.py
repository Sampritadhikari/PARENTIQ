from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("parent_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    parent = relationship("ParentProfile", back_populates="children")
    devices = relationship("Device", back_populates="child", cascade="all, delete-orphan")
    geofences = relationship("Geofence", back_populates="child", cascade="all, delete-orphan")
    screen_time_rules = relationship("ScreenTimeRule", back_populates="child", cascade="all, delete-orphan")
    app_restrictions = relationship("AppRestriction", back_populates="child", cascade="all, delete-orphan")
    safety_alerts = relationship("SafetyAlert", back_populates="child", cascade="all, delete-orphan")
    reports = relationship("ActivityReport", back_populates="child", cascade="all, delete-orphan")

