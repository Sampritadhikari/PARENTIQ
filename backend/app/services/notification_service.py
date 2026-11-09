import logging
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.safety import Notification
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        category: str,
        title: str,
        body: str,
        device_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            device_id=device_id,
            category=category,
            title=title,
            body=body,
            payload=payload or {},
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        # Log notification delivery
        logger.info(f"[NOTIF] Dispatched to user={user_id}: {title} - {body}")
        return notif


notification_service = NotificationService()

