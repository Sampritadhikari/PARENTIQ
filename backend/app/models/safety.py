from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class SafetyAlert(Base):
    __tablename__ = "safety_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    alert_type = Column(String(50), index=True, nullable=False)  # cyberbullying, inappropriate_web, keyword_alert, sos, suspicious_content
    severity = Column(String(20), default="warning", nullable=False)  # info, warning, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source_app = Column(String(255), nullable=True)  # e.g., YouTube, TikTok, Chrome, SMS
    matched_keyword = Column(String(100), nullable=True)
    url = Column(String(1024), nullable=True)
    meta_data = Column(JSON, nullable=True)
    is_reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    child = relationship("ChildProfile", back_populates="safety_alerts")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(50), index=True, nullable=False)  # location, battery, screentime, safety, app, device
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    device = relationship("Device", back_populates="notifications")

