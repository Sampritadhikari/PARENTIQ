from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SafetyAlertCreate(BaseModel):
    alert_type: str = Field(..., description="cyberbullying, inappropriate_web, keyword_alert, sos, suspicious_content")
    severity: str = Field("warning", description="info, warning, critical")
    title: str
    description: str
    source_app: Optional[str] = None
    matched_keyword: Optional[str] = None
    url: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class SafetyAlertOut(BaseModel):
    id: str
    child_id: str
    device_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    description: str
    source_app: Optional[str] = None
    matched_keyword: Optional[str] = None
    url: Optional[str] = None
    is_reviewed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: str
    category: str
    title: str
    body: str
    payload: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LiveSessionRequest(BaseModel):
    session_type: str = Field(..., description="screen_mirror, camera_stream, audio_listen, snapshot")


class LiveSessionConsent(BaseModel):
    session_token: str
    approved: bool


class LiveSessionOut(BaseModel):
    id: str
    device_id: str
    session_type: str
    status: str
    explicit_child_consent: bool
    session_token: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityReportOut(BaseModel):
    id: str
    child_id: str
    report_type: str
    report_date: date
    total_screen_time_seconds: int
    top_apps: List[Any]
    places_visited_count: int
    safety_alerts_count: int
    summary_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardSummaryOut(BaseModel):
    child_id: str
    child_name: str
    device_connected: bool
    battery_level: int
    is_charging: bool
    network_type: str
    last_seen_at: datetime
    today_screen_time_seconds: int
    daily_limit_minutes: int
    current_location: Optional[Dict[str, Any]] = None
    top_apps: List[Dict[str, Any]] = []
    unread_notifications_count: int
    unreviewed_safety_alerts_count: int
    instant_lock: bool

