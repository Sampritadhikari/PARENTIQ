from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_parent, get_db
from app.models.app_usage import AppUsage
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.location import LocationHistory
from app.models.parent import ParentProfile
from app.models.safety import SafetyAlert
from app.models.screentime import ScreenTimeLog
from app.schemas.safety import ActivityReportOut

router = APIRouter()


@router.get("/summary/{child_id}")
def get_activity_analytics(
    child_id: str,
    days: int = Query(7, ge=1, le=30),
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
    start_date = today - timedelta(days=days - 1)

    devices = db.query(Device).filter(Device.child_id == child.id).all()
    device_ids = [d.id for d in devices]

    # Daily Screen Time Trends
    st_logs = (
        db.query(ScreenTimeLog)
        .filter(
            ScreenTimeLog.device_id.in_(device_ids),
            ScreenTimeLog.log_date >= start_date,
        )
        .all()
    )

    day_map = {start_date + timedelta(days=i): 0 for i in range(days)}
    for log in st_logs:
        if log.log_date in day_map:
            day_map[log.log_date] += log.total_screen_time_seconds // 60  # in minutes

    trend_data = [
        {"date": d.isoformat(), "minutes": m, "day_of_week": d.strftime("%a")}
        for d, m in sorted(day_map.items())
    ]

    # Top apps in time range
    usages = (
        db.query(AppUsage)
        .filter(
            AppUsage.device_id.in_(device_ids),
            AppUsage.usage_date >= start_date,
        )
        .all()
    )

    app_totals: Dict[str, Dict[str, Any]] = {}
    category_totals: Dict[str, int] = {}
    for u in usages:
        if u.package_name not in app_totals:
            app_totals[u.package_name] = {
                "package_name": u.package_name,
                "app_name": u.app_name,
                "category": u.category,
                "seconds": 0,
            }
        app_totals[u.package_name]["seconds"] += u.foreground_time_seconds
        category_totals[u.category] = (
            category_totals.get(u.category, 0) + u.foreground_time_seconds
        )

    top_apps = sorted(
        app_totals.values(), key=lambda x: x["seconds"], reverse=True
    )[:5]

    categories_breakdown = [
        {"category": k, "minutes": v // 60}
        for k, v in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    ]

    # Safety activity count
    alerts_count = (
        db.query(SafetyAlert)
        .filter(
            SafetyAlert.child_id == child.id,
            SafetyAlert.created_at >= datetime.combine(start_date, datetime.min.time()),
        )
        .count()
    )

    # Location count
    places_count = (
        db.query(LocationHistory)
        .filter(
            LocationHistory.device_id.in_(device_ids),
            LocationHistory.recorded_at >= datetime.combine(start_date, datetime.min.time()),
        )
        .count()
    )

    return {
        "child_id": child.id,
        "child_name": child.name,
        "days": days,
        "screen_time_trend": trend_data,
        "top_apps": top_apps,
        "categories_breakdown": categories_breakdown,
        "total_safety_alerts": alerts_count,
        "locations_recorded": places_count,
    }

