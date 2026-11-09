from datetime import date, datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_parent, get_db
from app.models.app_usage import AppUsage
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.location import LocationHistory
from app.models.parent import ParentProfile
from app.models.safety import Notification, SafetyAlert
from app.models.screentime import ScreenTimeLog, ScreenTimeRule
from app.schemas.child import ChildCreate, ChildOut, ChildUpdate, DeviceOut, DeviceSummary
from app.schemas.safety import DashboardSummaryOut

router = APIRouter()


@router.get("", response_model=List[ChildOut])
def list_children(
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).all()
    return children


@router.post("", response_model=ChildOut, status_code=status.HTTP_201_CREATED)
def create_child(
    child_in: ChildCreate,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = ChildProfile(
        parent_id=parent.id,
        name=child_in.name,
        age=child_in.age,
        gender=child_in.gender,
        avatar_url=child_in.avatar_url,
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Initialize default screen time rules
    rule = ScreenTimeRule(child_id=child.id)
    db.add(rule)
    db.commit()

    return child


@router.get("/{child_id}", response_model=ChildOut)
def get_child(
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
    return child


@router.patch("/{child_id}", response_model=ChildOut)
def update_child(
    child_id: str,
    child_in: ChildUpdate,
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
    if child_in.name is not None:
        child.name = child_in.name
    if child_in.age is not None:
        child.age = child_in.age
    if child_in.gender is not None:
        child.gender = child_in.gender
    if child_in.avatar_url is not None:
        child.avatar_url = child_in.avatar_url
    db.commit()
    db.refresh(child)
    return child


@router.get("/{child_id}/devices", response_model=List[DeviceSummary])
def list_child_devices(
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
    return db.query(Device).filter(Device.child_id == child.id).all()


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
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
    db.delete(child)
    db.commit()
    return None


@router.get("/{child_id}/dashboard", response_model=DashboardSummaryOut)
def get_child_dashboard(
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

    # Primary connected device
    device = (
        db.query(Device)
        .filter(Device.child_id == child.id)
        .order_by(Device.last_seen_at.desc())
        .first()
    )

    today = date.today()
    screen_time_seconds = 0
    daily_limit = 120
    instant_lock = False

    rule = db.query(ScreenTimeRule).filter(ScreenTimeRule.child_id == child.id).first()
    if rule:
        daily_limit = rule.daily_limit_minutes
        instant_lock = rule.instant_lock

    curr_location = None
    top_apps = []

    if device:
        # Screen time today
        st_log = (
            db.query(ScreenTimeLog)
            .filter(
                ScreenTimeLog.device_id == device.id,
                ScreenTimeLog.log_date == today,
            )
            .first()
        )
        if st_log:
            screen_time_seconds = st_log.total_screen_time_seconds

        # Latest location
        latest_loc = (
            db.query(LocationHistory)
            .filter(LocationHistory.device_id == device.id)
            .order_by(LocationHistory.recorded_at.desc())
            .first()
        )
        if latest_loc:
            curr_location = {
                "latitude": latest_loc.latitude,
                "longitude": latest_loc.longitude,
                "accuracy": latest_loc.accuracy,
                "address": latest_loc.address,
                "recorded_at": latest_loc.recorded_at.isoformat(),
            }

        # Top 5 most used apps today
        usages = (
            db.query(AppUsage)
            .filter(
                AppUsage.device_id == device.id,
                AppUsage.usage_date == today,
            )
            .order_by(AppUsage.foreground_time_seconds.desc())
            .limit(5)
            .all()
        )
        top_apps = [
            {
                "package_name": u.package_name,
                "app_name": u.app_name,
                "category": u.category,
                "foreground_seconds": u.foreground_time_seconds,
            }
            for u in usages
        ]

    unread_notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == parent.user_id,
            Notification.is_read == False,
        )
        .count()
    )

    unreviewed_alerts = (
        db.query(SafetyAlert)
        .filter(
            SafetyAlert.child_id == child.id,
            SafetyAlert.is_reviewed == False,
        )
        .count()
    )

    return {
        "child_id": child.id,
        "child_name": child.name,
        "device_connected": device.is_online if device else False,
        "battery_level": device.battery_level if device else 0,
        "is_charging": device.is_charging if device else False,
        "network_type": device.network_type if device else "none",
        "last_seen_at": device.last_seen_at if device else datetime.now(timezone.utc),
        "today_screen_time_seconds": screen_time_seconds,
        "daily_limit_minutes": daily_limit,
        "current_location": curr_location,
        "top_apps": top_apps,
        "unread_notifications_count": unread_notifications,
        "unreviewed_safety_alerts_count": unreviewed_alerts,
        "instant_lock": instant_lock,
    }

