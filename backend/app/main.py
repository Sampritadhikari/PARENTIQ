import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.services.websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("parentiq")

# Ensure database tables exist
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Next-Generation Child Safety & Parental Control Platform REST & WebSocket API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/dashboard", tags=["Dashboard"])
def get_dashboard():
    dashboard_file = STATIC_DIR / "index.html"
    if dashboard_file.exists():
        return FileResponse(str(dashboard_file))
    return {"message": "Web dashboard static files not found."}


@app.get("/", tags=["Root"])
def root():
    return RedirectResponse(url="/dashboard")



# Real-Time WebSockets
@app.websocket("/ws/parent/{child_id}")
async def websocket_parent_endpoint(websocket: WebSocket, child_id: str):
    await ws_manager.connect_parent(child_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_parent(child_id, websocket)


@app.websocket("/ws/device/{device_id}")
async def websocket_device_endpoint(websocket: WebSocket, device_id: str):
    await ws_manager.connect_device(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_device(device_id)
