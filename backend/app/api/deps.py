from datetime import datetime, timezone
from typing import Generator, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.device import Device
from app.models.parent import ParentProfile
from app.models.pairing import DevicePairing
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject invalid",
        )
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive",
        )
    return user


def get_current_parent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ParentProfile:
    parent_profile = (
        db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    )
    if not parent_profile:
        # Auto-create parent profile if missing
        parent_profile = ParentProfile(user_id=current_user.id)
        db.add(parent_profile)
        db.commit()
        db.refresh(parent_profile)
    return parent_profile


def get_current_device(
    auth: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: Session = Depends(get_db),
) -> Device:
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device token required",
        )
    device_token = auth.credentials
    # Lookup device token in pairings table
    pairing = (
        db.query(DevicePairing)
        .filter(
            DevicePairing.device_token == device_token,
            DevicePairing.is_used == True,
        )
        .first()
    )
    if not pairing or not pairing.paired_device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device credentials or device unpaired",
        )
    device = db.query(Device).filter(Device.id == pairing.paired_device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    # Update last seen and online
    device.is_online = True
    device.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device

