from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ParentProfileOut(BaseModel):
    id: str
    user_id: str
    notification_preferences: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ChildCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=19)
    gender: Optional[str] = None
    avatar_url: Optional[str] = None


class ChildUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=19)
    gender: Optional[str] = None
    avatar_url: Optional[str] = None


class DeviceSummary(BaseModel):
    id: str
    device_name: str
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    is_online: bool
    battery_level: int
    is_charging: bool
    network_type: str
    last_seen_at: datetime

    class Config:
        from_attributes = True


class ChildOut(BaseModel):
    id: str
    parent_id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    devices: List[DeviceSummary] = []

    class Config:
        from_attributes = True


class DevicePermissionState(BaseModel):
    has_location_permission: bool = False
    has_background_location: bool = False
    has_usage_stats: bool = False
    has_accessibility: bool = False
    has_notification_listener: bool = False
    has_overlay_permission: bool = False
    has_battery_optimization_ignored: bool = False
    has_media_projection: bool = False


class DeviceHeartbeat(BaseModel):
    battery_level: int = Field(..., ge=0, le=100)
    is_charging: bool = False
    network_type: str = "wifi"
    permissions: Optional[DevicePermissionState] = None


class DeviceOut(BaseModel):
    id: str
    child_id: str
    device_name: str
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    device_fingerprint: str
    is_online: bool
    battery_level: int
    is_charging: bool
    network_type: str
    last_seen_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

