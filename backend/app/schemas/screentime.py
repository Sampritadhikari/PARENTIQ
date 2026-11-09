from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ScreenTimeRuleUpdate(BaseModel):
    daily_limit_minutes: Optional[int] = Field(None, ge=0, le=1440)
    school_mode_enabled: Optional[bool] = None
    school_mode_start: Optional[str] = None  # e.g. "08:30"
    school_mode_end: Optional[str] = None    # e.g. "15:30"
    school_mode_days: Optional[List[int]] = None
    bedtime_mode_enabled: Optional[bool] = None
    bedtime_start: Optional[str] = None      # e.g. "21:00"
    bedtime_end: Optional[str] = None        # e.g. "07:00"
    bedtime_days: Optional[List[int]] = None
    instant_lock: Optional[bool] = None


class ScreenTimeRuleOut(BaseModel):
    id: str
    child_id: str
    daily_limit_minutes: int
    school_mode_enabled: bool
    school_mode_start: Optional[str] = None
    school_mode_end: Optional[str] = None
    school_mode_days: List[int]
    bedtime_mode_enabled: bool
    bedtime_start: Optional[str] = None
    bedtime_end: Optional[str] = None
    bedtime_days: List[int]
    instant_lock: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class ScreenTimeSync(BaseModel):
    log_date: date
    total_screen_time_seconds: int
    unlock_count: int


class BonusTimeRequest(BaseModel):
    minutes_requested: int = Field(..., ge=5, le=180)
    reason: Optional[str] = None


class BonusTimeAction(BaseModel):
    minutes_granted: int = Field(..., ge=0, le=180)
    approved: bool


class ScreenTimeLogOut(BaseModel):
    id: str
    device_id: str
    log_date: date
    total_screen_time_seconds: int
    unlock_count: int
    extra_time_granted_minutes: int
    bonus_requests_pending: int
    updated_at: datetime

    class Config:
        from_attributes = True

