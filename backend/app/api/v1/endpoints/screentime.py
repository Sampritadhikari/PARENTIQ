from datetime import date, datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_current_parent, get_db
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.parent import ParentProfile
from app.models.screentime import ScreenTimeLog, ScreenTimeRule
from app.schemas.screentime import (
    BonusTimeAction,
    BonusTimeRequest,
    ScreenTimeLogOut,
    ScreenTimeRuleOut,
    ScreenTimeRuleUpdate,
    ScreenTimeSync,
)
from app.services.notification_service import notification_service
from app.services.websocket_manager import ws_manager

router = APIRouter()


@router.get("/rules/{child_id}", response_model=ScreenTimeRuleOut)
def get_rules(
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
    rule = db.query(ScreenTimeRule).filter(ScreenTimeRule.child_id == child.id).first()
    if not rule:
        rule = ScreenTimeRule(child_id=child.id)
        db.add(rule)
        db.commit()
        db.refresh(rule)
    return rule


@router.patch("/rules/{child_id}", response_model=ScreenTimeRuleOut)
async def update_rules(
    child_id: str,
    update_in: ScreenTimeRuleUpdate,
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
    rule = db.query(ScreenTimeRule).filter(ScreenTimeRule.child_id == child.id).first()
    if not rule:
        rule = ScreenTimeRule(child_id=child.id)
        db.add(rule)

    for field, val in update_in.model_dump(exclude_unset=True).items():
        setattr(rule, field, val)

    db.commit()
    db.refresh(rule)

    # Notify child devices via WebSocket of rule update
    devices = db.query(Device).filter(Device.child_id == child.id).all()
    for dev in devices:
        await ws_manager.send_to_device(
            dev.id,
            {
                "type": "rules_updated",
                "daily_limit_minutes": rule.daily_limit_minutes,
                "school_mode": rule.school_mode_enabled,
                "bedtime_mode": rule.bedtime_mode_enabled,
                "instant_lock": rule.instant_lock,
            },
        )

    return rule


@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_screentime(
    sync_in: ScreenTimeSync,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    log = (
        db.query(ScreenTimeLog)
        .filter(
            ScreenTimeLog.device_id == device.id,
            ScreenTimeLog.log_date == sync_in.log_date,
        )
        .first()
    )
    if not log:
        log = ScreenTimeLog(
            device_id=device.id,
            log_date=sync_in.log_date,
            total_screen_time_seconds=sync_in.total_screen_time_seconds,
            unlock_count=sync_in.unlock_count,
        )
        db.add(log)
    else:
        log.total_screen_time_seconds = sync_in.total_screen_time_seconds
        log.unlock_count = sync_in.unlock_count

    db.commit()
    return {"status": "synced"}


@router.post("/bonus-request", status_code=status.HTTP_200_OK)
async def request_bonus_time(
    req: BonusTimeRequest,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    today = date.today()
    log = (
        db.query(ScreenTimeLog)
        .filter(
            ScreenTimeLog.device_id == device.id,
            ScreenTimeLog.log_date == today,
        )
        .first()
    )
    if not log:
        log = ScreenTimeLog(device_id=device.id, log_date=today)
        db.add(log)
        db.flush()

    log.bonus_requests_pending += 1
    db.commit()

    child = db.query(ChildProfile).filter(ChildProfile.id == device.child_id).first()
    parent = (
        db.query(ParentProfile).filter(ParentProfile.id == child.parent_id).first()
        if child
        else None
    )
    if parent:
        notification_service.create_notification(
            db=db,
            user_id=parent.user_id,
            category="screentime",
            title="Screen Time Extension Request",
            body=f"{child.name} requested {req.minutes_requested} additional minutes of screen time.",
            device_id=device.id,
            payload={
                "minutes_requested": req.minutes_requested,
                "reason": req.reason,
                "child_id": child.id,
            },
        )

        await ws_manager.broadcast_to_parents(
            child.id,
            {
                "type": "bonus_time_requested",
                "minutes": req.minutes_requested,
                "reason": req.reason,
            },
        )

    return {"status": "request_delivered"}


@router.post("/bonus-action/{child_id}", status_code=status.HTTP_200_OK)
async def grant_bonus_time(
    child_id: str,
    action: BonusTimeAction,
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

    today = date.today()
    devices = db.query(Device).filter(Device.child_id == child.id).all()
    for dev in devices:
        log = (
            db.query(ScreenTimeLog)
            .filter(
                ScreenTimeLog.device_id == dev.id,
                ScreenTimeLog.log_date == today,
            )
            .first()
        )
        if log:
            if action.approved:
                log.extra_time_granted_minutes += action.minutes_granted
            log.bonus_requests_pending = max(0, log.bonus_requests_pending - 1)

        await ws_manager.send_to_device(
            dev.id,
            {
                "type": "bonus_time_decision",
                "approved": action.approved,
                "minutes_granted": action.minutes_granted if action.approved else 0,
            },
        )

    db.commit()
    return {"status": "processed", "approved": action.approved}

