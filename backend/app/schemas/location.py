from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LocationLogCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    altitude: Optional[float] = None
    battery_level: Optional[int] = None
    provider: str = "gps"
    address: Optional[str] = None
    recorded_at: Optional[datetime] = None


class LocationBatchCreate(BaseModel):
    locations: List[LocationLogCreate]


class LocationLogOut(BaseModel):
    id: str
    device_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    altitude: Optional[float] = None
    battery_level: Optional[int] = None
    provider: str
    address: Optional[str] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


class GeofenceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    zone_type: str = Field("safe", description="safe, dangerous, restricted")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_meters: float = Field(200.0, ge=20.0, le=50000.0)
    notify_on_entry: bool = True
    notify_on_exit: bool = True


class GeofenceOut(BaseModel):
    id: str
    child_id: str
    name: str
    zone_type: str
    latitude: float
    longitude: float
    radius_meters: float
    notify_on_entry: bool
    notify_on_exit: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

