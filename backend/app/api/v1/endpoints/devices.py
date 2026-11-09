from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_current_parent, get_db
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.parent import ParentProfile
from app.models.pairing import DevicePermission
from app.schemas.child import DeviceHeartbeat, DeviceOut

router = APIRouter()


@router.post("/heartbeat", status_code=status.HTTP_200_OK)
def device_heartbeat(
    heartbeat: DeviceHeartbeat,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    device.battery_level = heartbeat.battery_level
    device.is_charging = heartbeat.is_charging
    device.network_type = heartbeat.network_type
    device.is_online = True
    device.last_seen_at = now

    if heartbeat.permissions:
        perms = (
            db.query(DevicePermission)
            .filter(DevicePermission.device_id == device.id)
            .first()
        )
        if not perms:
            perms = DevicePermission(device_id=device.id)
            db.add(perms)

        p = heartbeat.permissions
        perms.has_location_permission = p.has_location_permission
        perms.has_background_location = p.has_background_location
        perms.has_usage_stats = p.has_usage_stats
        perms.has_accessibility = p.has_accessibility
        perms.has_notification_listener = p.has_notification_listener
        perms.has_overlay_permission = p.has_overlay_permission
        perms.has_battery_optimization_ignored = p.has_battery_optimization_ignored
        perms.has_media_projection = p.has_media_projection
        perms.updated_at = now

    db.commit()
    return {"status": "ok", "server_time": now.isoformat()}


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(
    device_id: str,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    device = (
        db.query(Device)
        .join(ChildProfile)
        .filter(
            Device.id == device_id,
            ChildProfile.parent_id == parent.id,
        )
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
        )
    return device


@router.get("/{device_id}/permissions")
def get_device_permissions(
    device_id: str,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    device = (
        db.query(Device)
        .join(ChildProfile)
        .filter(
            Device.id == device_id,
            ChildProfile.parent_id == parent.id,
        )
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
        )
    perms = (
        db.query(DevicePermission)
        .filter(DevicePermission.device_id == device.id)
        .first()
    )
    if not perms:
        return {}
    return {
        "has_location_permission": perms.has_location_permission,
        "has_background_location": perms.has_background_location,
        "has_usage_stats": perms.has_usage_stats,
        "has_accessibility": perms.has_accessibility,
        "has_notification_listener": perms.has_notification_listener,
        "has_overlay_permission": perms.has_overlay_permission,
        "has_battery_optimization_ignored": perms.has_battery_optimization_ignored,
        "has_media_projection": perms.has_media_projection,
        "updated_at": perms.updated_at,
    }

