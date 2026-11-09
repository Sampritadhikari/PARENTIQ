from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_current_parent, get_db
from app.core.security import generate_secure_token
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.monitoring import LiveSession
from app.models.parent import ParentProfile
from app.schemas.safety import LiveSessionConsent, LiveSessionOut, LiveSessionRequest
from app.services.websocket_manager import ws_manager

router = APIRouter()


class SnapshotUpload(BaseModel):
    session_token: str
    image_base64: str


@router.post("/request/{device_id}", response_model=LiveSessionOut)
async def request_live_session(
    device_id: str,
    req: LiveSessionRequest,
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

    # Invalidate any old active sessions on this device
    db.query(LiveSession).filter(
        LiveSession.device_id == device.id,
        LiveSession.status.in_(["requested", "approved", "active"]),
    ).update({"status": "ended", "ended_at": datetime.now(timezone.utc)})

    token = generate_secure_token(24)
    session = LiveSession(
        device_id=device.id,
        session_type=req.session_type,
        status="requested",
        explicit_child_consent=False,
        session_token=token,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Dispatch explicit permission request prompt to child device
    sent = await ws_manager.send_to_device(
        device.id,
        {
            "type": "live_session_request",
            "session_id": session.id,
            "session_type": req.session_type,
            "session_token": token,
            "notice": "Parent requested an approved live monitoring session. Your device will display a visible indicator.",
        },
    )

    return session


@router.post("/consent", status_code=status.HTTP_200_OK)
async def submit_child_consent(
    consent: LiveSessionConsent,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    session = (
        db.query(LiveSession)
        .filter(
            LiveSession.session_token == consent.session_token,
            LiveSession.device_id == device.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Live session request not found"
        )

    now = datetime.now(timezone.utc)
    if consent.approved:
        session.status = "active"
        session.explicit_child_consent = True
        session.started_at = now
    else:
        session.status = "rejected"
        session.explicit_child_consent = False
        session.ended_at = now

    db.commit()
    db.refresh(session)

    # Broadcast session approval status to parents
    await ws_manager.broadcast_to_parents(
        device.child_id,
        {
            "type": "live_session_decision",
            "session_id": session.id,
            "approved": consent.approved,
            "session_token": session.session_token,
        },
    )

    return {"status": session.status, "session_id": session.id}


@router.post("/terminate/{session_id}", status_code=status.HTTP_200_OK)
async def terminate_live_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    session = db.query(LiveSession).filter(LiveSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found"
        )

    session.status = "ended"
    session.ended_at = datetime.now(timezone.utc)
    db.commit()

    device = db.query(Device).filter(Device.id == session.device_id).first()
    if device:
        # Notify both child device and parent WebSocket listeners to stop streams
        await ws_manager.send_to_device(
            device.id,
            {"type": "live_session_terminated", "session_id": session.id},
        )
        await ws_manager.broadcast_to_parents(
            device.child_id,
            {"type": "live_session_terminated", "session_id": session.id},
        )

    return {"status": "terminated"}


@router.get("/status/{session_id}", response_model=LiveSessionOut)
def get_session_status(
    session_id: str,
    db: Session = Depends(get_db),
):
    session = db.query(LiveSession).filter(LiveSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session

