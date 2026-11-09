from datetime import datetime, timedelta, timezone
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_parent, get_db
from app.core.config import settings
from app.core.security import generate_pairing_code, generate_secure_token
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.parent import ParentProfile
from app.models.pairing import DevicePairing, DevicePermission
from app.schemas.pairing import (
    PairingInitResponse,
    PairingVerifyRequest,
    PairingVerifyResponse,
)

router = APIRouter()


@router.post("/initiate/{child_id}", response_model=PairingInitResponse)
def initiate_pairing(
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

    # Invalidate previous unused pairing codes for this child
    db.query(DevicePairing).filter(
        DevicePairing.child_id == child.id,
        DevicePairing.is_used == False,
    ).update({"is_used": True})
    db.commit()

    code = generate_pairing_code()
    device_token = generate_secure_token(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PAIRING_CODE_EXPIRE_MINUTES
    )

    pairing = DevicePairing(
        child_id=child.id,
        pairing_code=code,
        device_token=device_token,
        expires_at=expires_at,
        is_used=False,
    )
    db.add(pairing)
    db.commit()

    qr_payload = json.dumps({
        "server": settings.API_V1_STR,
        "child_id": child.id,
        "code": code,
        "expires_at": expires_at.isoformat(),
    })

    return {
        "pairing_code": code,
        "expires_at": expires_at,
        "child_id": child.id,
        "child_name": child.name,
        "qr_payload": qr_payload,
    }


@router.post("/verify", response_model=PairingVerifyResponse)
def verify_pairing(
    req: PairingVerifyRequest,
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    # Strip any formatting hyphens
    clean_code = req.pairing_code.replace("-", "").strip()

    pairing = (
        db.query(DevicePairing)
        .filter(
            DevicePairing.pairing_code == clean_code,
            DevicePairing.is_used == False,
        )
        .first()
    )

    if not pairing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used pairing code",
        )

    # Check expiration
    exp = pairing.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pairing code has expired. Please generate a new code from the parent app.",
        )

    # Check attempt limit
    if pairing.attempts >= settings.PAIRING_MAX_ATTEMPTS:
        pairing.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum pairing attempts exceeded for this code.",
        )

    child = db.query(ChildProfile).filter(ChildProfile.id == pairing.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found"
        )

    # Find or create device by fingerprint
    device = (
        db.query(Device)
        .filter(Device.device_fingerprint == req.device_fingerprint)
        .first()
    )
    if device:
        device.child_id = child.id
        device.device_name = req.device_name
        device.device_model = req.device_model
        device.os_version = req.os_version
        device.app_version = req.app_version
        device.fcm_token = req.fcm_token
        device.is_online = True
        device.last_seen_at = now
    else:
        device = Device(
            child_id=child.id,
            device_name=req.device_name,
            device_model=req.device_model,
            os_version=req.os_version,
            app_version=req.app_version,
            device_fingerprint=req.device_fingerprint,
            fcm_token=req.fcm_token,
            is_online=True,
            battery_level=100,
            last_seen_at=now,
        )
        db.add(device)
        db.flush()

        # Initialize permissions record
        permission = DevicePermission(device_id=device.id)
        db.add(permission)

    pairing.is_used = True
    pairing.paired_device_id = device.id
    db.commit()
    db.refresh(device)

    return {
        "device_id": device.id,
        "device_token": pairing.device_token,
        "child_id": child.id,
        "child_name": child.name,
        "paired_at": now,
        "server_time": now,
    }


@router.post("/revoke/{device_id}", status_code=status.HTTP_200_OK)
def revoke_device(
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

    # Invalidate all pairing tokens for this device
    db.query(DevicePairing).filter(DevicePairing.paired_device_id == device.id).update(
        {"is_used": True}
    )
    device.is_online = False
    db.commit()
    return {"message": "Device pairing revoked successfully"}

