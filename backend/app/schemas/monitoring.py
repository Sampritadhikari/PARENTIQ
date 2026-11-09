from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


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

