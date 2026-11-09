from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class InstalledAppCreate(BaseModel):
    package_name: str
    app_name: str
    version_name: Optional[str] = None
    version_code: Optional[int] = None
    category: str = "Other"
    is_system_app: bool = False
    installed_at: Optional[datetime] = None


class InstalledAppBatch(BaseModel):
    apps: List[InstalledAppCreate]


class InstalledAppOut(BaseModel):
    id: str
    package_name: str
    app_name: str
    version_name: Optional[str] = None
    category: str
    is_system_app: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AppUsageCreate(BaseModel):
    package_name: str
    app_name: str
    category: str = "Other"
    usage_date: date
    foreground_time_seconds: int
    launch_count: int
    last_time_used: Optional[datetime] = None


class AppUsageBatch(BaseModel):
    usages: List[AppUsageCreate]


class AppUsageOut(BaseModel):
    id: str
    package_name: str
    app_name: str
    category: str
    usage_date: date
    foreground_time_seconds: int
    launch_count: int
    last_time_used: Optional[datetime] = None

    class Config:
        from_attributes = True


class AppRestrictionUpdate(BaseModel):
    package_name: str
    app_name: str
    is_blocked: bool
    daily_limit_minutes: Optional[int] = None
    block_during_school: bool = True
    block_during_bedtime: bool = True


class AppRestrictionOut(BaseModel):
    id: str
    child_id: str
    package_name: str
    app_name: str
    is_blocked: bool
    daily_limit_minutes: Optional[int] = None
    block_during_school: bool
    block_during_bedtime: bool
    updated_at: datetime

    class Config:
        from_attributes = True

