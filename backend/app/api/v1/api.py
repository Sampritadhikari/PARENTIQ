from fastapi import APIRouter

from app.api.v1.endpoints import (
    apps,
    auth,
    children,
    devices,
    location,
    monitoring,
    notifications,
    pairing,
    reports,
    screentime,
    safety,
    settings,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(children.router, prefix="/children", tags=["Children & Dashboard"])
api_router.include_router(devices.router, prefix="/devices", tags=["Device Management"])
api_router.include_router(pairing.router, prefix="/pairing", tags=["Device Pairing"])
api_router.include_router(location.router, prefix="/location", tags=["Location & Geofencing"])
api_router.include_router(screentime.router, prefix="/screentime", tags=["Screen Time"])
api_router.include_router(apps.router, prefix="/apps", tags=["Application Management"])
api_router.include_router(safety.router, prefix="/safety", tags=["Online Safety & SOS"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Live Monitoring"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["Analytics & Reports"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings & Preferences"])

