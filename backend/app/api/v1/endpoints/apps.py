from datetime import date, datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_current_parent, get_db
from app.models.app_usage import AppRestriction, AppUsage, InstalledApp
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.parent import ParentProfile
from app.schemas.apps import (
    AppRestrictionOut,
    AppRestrictionUpdate,
    AppUsageBatch,
    AppUsageOut,
    InstalledAppBatch,
    InstalledAppOut,
)
from app.services.notification_service import notification_service
from app.services.websocket_manager import ws_manager

router = APIRouter()


@router.post("/inventory", status_code=status.HTTP_200_OK)
def sync_installed_apps(
    batch: InstalledAppBatch,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    existing_packages = {
        app.package_name
        for app in db.query(InstalledApp).filter(InstalledApp.device_id == device.id).all()
    }

    new_apps_count = 0
    now = datetime.now(timezone.utc)
    child = db.query(ChildProfile).filter(ChildProfile.id == device.child_id).first()
    parent = (
        db.query(ParentProfile).filter(ParentProfile.id == child.parent_id).first()
        if child
        else None
    )

    for item in batch.apps:
        if item.package_name not in existing_packages:
            new_app = InstalledApp(
                device_id=device.id,
                package_name=item.package_name,
                app_name=item.app_name,
                version_name=item.version_name,
                version_code=item.version_code,
                category=item.category,
                is_system_app=item.is_system_app,
                installed_at=item.installed_at or now,
            )
            db.add(new_app)
            new_apps_count += 1

            # Dispatch newly installed app notification to parent
            if parent and not item.is_system_app:
                notification_service.create_notification(
                    db=db,
                    user_id=parent.user_id,
                    category="app",
                    title="New App Installed",
                    body=f"{child.name} installed a new app: {item.app_name}",
                    device_id=device.id,
                    payload={"package_name": item.package_name, "app_name": item.app_name},
                )

    db.commit()
    return {"status": "synced", "new_apps_detected": new_apps_count}


@router.post("/usage", status_code=status.HTTP_200_OK)
def sync_app_usage(
    batch: AppUsageBatch,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    for u in batch.usages:
        record = (
            db.query(AppUsage)
            .filter(
                AppUsage.device_id == device.id,
                AppUsage.package_name == u.package_name,
                AppUsage.usage_date == u.usage_date,
            )
            .first()
        )
        if not record:
            record = AppUsage(
                device_id=device.id,
                package_name=u.package_name,
                app_name=u.app_name,
                category=u.category,
                usage_date=u.usage_date,
                foreground_time_seconds=u.foreground_time_seconds,
                launch_count=u.launch_count,
                last_time_used=u.last_time_used,
            )
            db.add(record)
        else:
            record.foreground_time_seconds = u.foreground_time_seconds
            record.launch_count = u.launch_count
            record.last_time_used = u.last_time_used

    db.commit()
    return {"status": "synced", "count": len(batch.usages)}


@router.get("/installed/{child_id}", response_model=List[InstalledAppOut])
def get_installed_apps(
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

    apps = (
        db.query(InstalledApp)
        .join(Device)
        .filter(Device.child_id == child.id)
        .order_by(InstalledApp.app_name.asc())
        .all()
    )
    return apps


@router.get("/usage/{child_id}", response_model=List[AppUsageOut])
def get_usage_stats(
    child_id: str,
    target_date: date = Query(default_factory=date.today),
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

    usages = (
        db.query(AppUsage)
        .join(Device)
        .filter(Device.child_id == child.id, AppUsage.usage_date == target_date)
        .order_by(AppUsage.foreground_time_seconds.desc())
        .all()
    )
    return usages


@router.post("/restrictions/{child_id}", response_model=AppRestrictionOut)
async def set_app_restriction(
    child_id: str,
    restriction_in: AppRestrictionUpdate,
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

    rule = (
        db.query(AppRestriction)
        .filter(
            AppRestriction.child_id == child.id,
            AppRestriction.package_name == restriction_in.package_name,
        )
        .first()
    )
    if not rule:
        rule = AppRestriction(
            child_id=child.id,
            package_name=restriction_in.package_name,
            app_name=restriction_in.app_name,
            is_blocked=restriction_in.is_blocked,
            daily_limit_minutes=restriction_in.daily_limit_minutes,
            block_during_school=restriction_in.block_during_school,
            block_during_bedtime=restriction_in.block_during_bedtime,
        )
        db.add(rule)
    else:
        rule.is_blocked = restriction_in.is_blocked
        rule.daily_limit_minutes = restriction_in.daily_limit_minutes
        rule.block_during_school = restriction_in.block_during_school
        rule.block_during_bedtime = restriction_in.block_during_bedtime

    db.commit()
    db.refresh(rule)

    # Sync rule to devices in real time
    devices = db.query(Device).filter(Device.child_id == child.id).all()
    for dev in devices:
        await ws_manager.send_to_device(
            dev.id,
            {
                "type": "app_restriction_updated",
                "package_name": rule.package_name,
                "is_blocked": rule.is_blocked,
                "limit_minutes": rule.daily_limit_minutes,
            },
        )

    return rule


@router.get("/restrictions/{child_id}", response_model=List[AppRestrictionOut])
def get_app_restrictions(
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

    return db.query(AppRestriction).filter(AppRestriction.child_id == child.id).all()

