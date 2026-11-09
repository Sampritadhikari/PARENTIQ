from datetime import datetime, timezone
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_current_parent, get_db
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.location import Geofence, LocationHistory
from app.models.parent import ParentProfile
from app.models.safety import Notification
from app.schemas.location import (
    GeofenceCreate,
    GeofenceOut,
    LocationBatchCreate,
    LocationLogCreate,
    LocationLogOut,
)
from app.services.websocket_manager import ws_manager

router = APIRouter()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two lat/lon coordinates."""
    r = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def check_geofence_events(
    db: Session, child_id: str, lat: float, lon: float, device: Device
):
    """Check child current coordinate against active geofences and create alerts safely."""
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        return

    parent = db.query(ParentProfile).filter(ParentProfile.id == child.parent_id).first()
    if not parent:
        return

    geofences = (
        db.query(Geofence)
        .filter(Geofence.child_id == child_id, Geofence.is_active == True)
        .all()
    )

    new_notifications = []
    for gf in geofences:
        dist = haversine_distance(lat, lon, gf.latitude, gf.longitude)
        is_inside = dist <= gf.radius_meters
        if is_inside and gf.notify_on_entry:
            notif = Notification(
                user_id=parent.user_id,
                device_id=device.id,
                category="location",
                title=f"Entered Safe Zone: {gf.name}",
                body=f"{child.name} has arrived at {gf.name}.",
                payload={"geofence_id": gf.id, "event": "enter", "lat": lat, "lon": lon},
            )
            new_notifications.append(notif)

    if new_notifications:
        db.add_all(new_notifications)
        db.commit()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def post_location_batch(
    batch: LocationBatchCreate,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    latest_item = None
    for item in batch.locations:
        rec_time = item.recorded_at or now
        loc = LocationHistory(
            device_id=device.id,
            latitude=item.latitude,
            longitude=item.longitude,
            accuracy=item.accuracy,
            speed=item.speed,
            altitude=item.altitude,
            battery_level=item.battery_level,
            provider=item.provider,
            address=item.address,
            recorded_at=rec_time,
        )
        db.add(loc)
        latest_item = loc

    db.commit()

    if latest_item:
        check_geofence_events(
            db, device.child_id, latest_item.latitude, latest_item.longitude, device
        )
        await ws_manager.broadcast_to_parents(
            device.child_id,
            {
                "type": "location_update",
                "latitude": latest_item.latitude,
                "longitude": latest_item.longitude,
                "accuracy": latest_item.accuracy,
                "recorded_at": latest_item.recorded_at.isoformat(),
            },
        )

    return {"count": len(batch.locations), "status": "recorded"}


@router.get("/current/{child_id}", response_model=Optional[LocationLogOut])
def get_current_location(
    child_id: str,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = (
        db.query(ChildProfile)
        .filter(ChildProfile.id == child_id, ChildProfile.parent_id == parent.id)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found"
        )

    latest_loc = (
        db.query(LocationHistory)
        .join(Device)
        .filter(Device.child_id == child.id)
        .order_by(LocationHistory.recorded_at.desc())
        .first()
    )
    return latest_loc


@router.get("/history/{child_id}", response_model=List[LocationLogOut])
def get_location_history(
    child_id: str,
    limit: int = Query(50, ge=1, le=500),
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = (
        db.query(ChildProfile)
        .filter(ChildProfile.id == child_id, ChildProfile.parent_id == parent.id)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found"
        )

    history = (
        db.query(LocationHistory)
        .join(Device)
        .filter(Device.child_id == child.id)
        .order_by(LocationHistory.recorded_at.desc())
        .limit(limit)
        .all()
    )
    return history


@router.get("/geofences/{child_id}", response_model=List[GeofenceOut])
def list_geofences(
    child_id: str,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = (
        db.query(ChildProfile)
        .filter(ChildProfile.id == child_id, ChildProfile.parent_id == parent.id)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found"
        )

    return db.query(Geofence).filter(Geofence.child_id == child.id).all()


@router.post("/geofences/{child_id}", response_model=GeofenceOut, status_code=status.HTTP_201_CREATED)
def create_geofence(
    child_id: str,
    gf_in: GeofenceCreate,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = (
        db.query(ChildProfile)
        .filter(ChildProfile.id == child_id, ChildProfile.parent_id == parent.id)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found"
        )

    gf = Geofence(
        child_id=child.id,
        name=gf_in.name,
        zone_type=gf_in.zone_type,
        latitude=gf_in.latitude,
        longitude=gf_in.longitude,
        radius_meters=gf_in.radius_meters,
        notify_on_entry=gf_in.notify_on_entry,
        notify_on_exit=gf_in.notify_on_exit,
        is_active=True,
    )
    db.add(gf)
    db.commit()
    db.refresh(gf)
    return gf


@router.delete("/geofences/{geofence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_geofence(
    geofence_id: str,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    gf = (
        db.query(Geofence)
        .join(ChildProfile)
        .filter(
            Geofence.id == geofence_id,
            ChildProfile.parent_id == parent.id,
        )
        .first()
    )
    if not gf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Geofence not found"
        )
    db.delete(gf)
    db.commit()
    return None
