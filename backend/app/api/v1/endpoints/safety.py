from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_device, get_current_parent, get_db
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.parent import ParentProfile
from app.models.safety import SafetyAlert
from app.schemas.safety import SafetyAlertCreate, SafetyAlertOut
from app.services.notification_service import notification_service
from app.services.safety_analyzer import safety_analyzer
from app.services.websocket_manager import ws_manager

router = APIRouter()


class URLInspectionRequest(BaseModel):
    url: str
    source_app: str = "Browser"


class ContentInspectionRequest(BaseModel):
    content: str
    source_app: str  # WhatsApp, SMS, Instagram, Discord, etc.


@router.post("/inspect-url")
def inspect_url(
    req: URLInspectionRequest,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    analysis = safety_analyzer.inspect_url(req.url)
    if analysis:
        child = db.query(ChildProfile).filter(ChildProfile.id == device.child_id).first()
        parent = (
            db.query(ParentProfile).filter(ParentProfile.id == child.parent_id).first()
            if child
            else None
        )

        alert = SafetyAlert(
            child_id=device.child_id,
            device_id=device.id,
            alert_type="inappropriate_web",
            severity=analysis["severity"],
            title="Inappropriate Web Domain Blocked",
            description=analysis["description"],
            source_app=req.source_app,
            matched_keyword=analysis["matched_keyword"],
            url=req.url,
        )
        db.add(alert)
        db.commit()

        if parent:
            notification_service.create_notification(
                db=db,
                user_id=parent.user_id,
                category="safety",
                title="Online Safety Alert",
                body=f"{child.name} attempted to visit a restricted website: {req.url}",
                device_id=device.id,
                payload={"alert_id": alert.id, "url": req.url},
            )

        return {"blocked": True, "reason": analysis["description"]}
    return {"blocked": False, "reason": "allowed"}


@router.post("/inspect-content")
def inspect_content(
    req: ContentInspectionRequest,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    analysis = safety_analyzer.inspect_text(req.content)
    if analysis:
        child = db.query(ChildProfile).filter(ChildProfile.id == device.child_id).first()
        parent = (
            db.query(ParentProfile).filter(ParentProfile.id == child.parent_id).first()
            if child
            else None
        )

        alert = SafetyAlert(
            child_id=device.child_id,
            device_id=device.id,
            alert_type="cyberbullying" if "hate" in analysis["category"] else "keyword_alert",
            severity=analysis["severity"],
            title=f"Potential {analysis['category'].replace('_', ' ').title()} Alert",
            description=f"Sensitive term detected in {req.source_app}: '{analysis['matched_keyword']}'",
            source_app=req.source_app,
            matched_keyword=analysis["matched_keyword"],
        )
        db.add(alert)
        db.commit()

        if parent:
            notification_service.create_notification(
                db=db,
                user_id=parent.user_id,
                category="safety",
                title=f"Safety Warning: {child.name}",
                body=f"Harmful or bullying message detected in {req.source_app}.",
                device_id=device.id,
                payload={"alert_id": alert.id, "source_app": req.source_app},
            )

        return {"flagged": True, "category": analysis["category"]}
    return {"flagged": False}


@router.post("/sos", status_code=status.HTTP_201_CREATED)
async def trigger_emergency_sos(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    child = db.query(ChildProfile).filter(ChildProfile.id == device.child_id).first()
    parent = (
        db.query(ParentProfile).filter(ParentProfile.id == child.parent_id).first()
        if child
        else None
    )

    alert = SafetyAlert(
        child_id=device.child_id,
        device_id=device.id,
        alert_type="sos",
        severity="critical",
        title="EMERGENCY SOS TRIGGERED!",
        description=f"{child.name} activated the Emergency SOS alert on their device.",
        source_app="PARENTIQ Child Companion",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    if parent:
        notification_service.create_notification(
            db=db,
            user_id=parent.user_id,
            category="safety",
            title="EMERGENCY SOS ALERT!",
            body=f"{child.name} has pressed the Emergency SOS button!",
            device_id=device.id,
            payload={"alert_id": alert.id, "emergency": True},
        )

        # Broadcast critical SOS alert across WebSockets to parent
        await ws_manager.broadcast_to_parents(
            child.id,
            {
                "type": "sos_alert",
                "alert_id": alert.id,
                "child_name": child.name,
                "timestamp": alert.created_at.isoformat(),
            },
        )

    return {"status": "sos_broadcasted", "alert_id": alert.id}


@router.get("/alerts/{child_id}", response_model=List[SafetyAlertOut])
def get_safety_alerts(
    child_id: str,
    limit: int = Query(50, ge=1, le=200),
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

    alerts = (
        db.query(SafetyAlert)
        .filter(SafetyAlert.child_id == child.id)
        .order_by(SafetyAlert.created_at.desc())
        .limit(limit)
        .all()
    )
    return alerts


@router.patch("/alerts/{alert_id}/review", response_model=SafetyAlertOut)
def review_safety_alert(
    alert_id: str,
    parent: ParentProfile = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    alert = (
        db.query(SafetyAlert)
        .join(ChildProfile)
        .filter(
            SafetyAlert.id == alert_id,
            ChildProfile.parent_id == parent.id,
        )
        .first()
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Safety alert not found"
        )

    alert.is_reviewed = True
    alert.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert

