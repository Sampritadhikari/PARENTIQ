from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_parent, get_current_user, get_db
from app.core.security import get_password_hash, verify_password
from app.models.parent import ParentProfile
from app.models.user import User

router = APIRouter()


class NotificationPreferencesUpdate(BaseModel):
    location_alerts: Optional[bool] = None
    geofence_alerts: Optional[bool] = None
    screentime_alerts: Optional[bool] = None
    app_install_alerts: Optional[bool] = None
    safety_keyword_alerts: Optional[bool] = None
    battery_alerts: Optional[bool] = None
    device_offline_alerts: Optional[bool] = None


class ParentPinSet(BaseModel):
    pin: str


class ParentPinVerify(BaseModel):
    pin: str


@router.get("/preferences")
def get_preferences(parent: ParentProfile = Depends(get_current_parent)):
    return parent.notification_preferences


@router.patch("/preferences")
def update_preferences(
    prefs: NotificationPreferencesUpdate,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    current = dict(parent.notification_preferences)
    for k, v in prefs.model_dump(exclude_unset=True).items():
        current[k] = v
    parent.notification_preferences = current
    db.commit()
    return parent.notification_preferences


@router.post("/set-pin")
def set_parent_pin(
    pin_in: ParentPinSet,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    if len(pin_in.pin) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN must be at least 4 digits",
        )
    parent.pin_hash = get_password_hash(pin_in.pin)
    db.commit()
    return {"message": "Parent security PIN set successfully"}


@router.post("/verify-pin")
def verify_parent_pin(
    pin_in: ParentPinVerify,
    parent: ParentProfile = Depends(get_current_parent),
):
    if not parent.pin_hash:
        return {"has_pin": False, "valid": True}
    valid = verify_password(pin_in.pin, parent.pin_hash)
    return {"has_pin": True, "valid": valid}

