from datetime import date, datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    session_type = Column(String(50), nullable=False)  # screen_mirror, camera_stream, audio_listen, snapshot
    status = Column(String(30), default="requested", nullable=False)  # requested, approved, active, ended, rejected
    explicit_child_consent = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    terminated_by = Column(String(50), nullable=True)  # parent, child, timeout, disconnect
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    device = relationship("Device", back_populates="live_sessions")


class ActivityReport(Base):
    __tablename__ = "activity_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    report_type = Column(String(20), default="daily", nullable=False)  # daily, weekly
    report_date = Column(Date, default=lambda: date.today(), index=True, nullable=False)
    total_screen_time_seconds = Column(Integer, default=0, nullable=False)
    top_apps = Column(JSON, default=list, nullable=False)
    places_visited_count = Column(Integer, default=0, nullable=False)
    safety_alerts_count = Column(Integer, default=0, nullable=False)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    child = relationship("ChildProfile", back_populates="reports")


from app.models.audit import AuditLog  # noqa: E402
