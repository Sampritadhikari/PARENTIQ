from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PairingInitResponse(BaseModel):
    pairing_code: str  # 6-digit PIN
    expires_at: datetime
    child_id: str
    child_name: str
    qr_payload: str


class PairingVerifyRequest(BaseModel):
    pairing_code: str = Field(..., min_length=6, max_length=10)
    device_name: str = Field(..., min_length=1, max_length=100)
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    device_fingerprint: str = Field(..., min_length=5, max_length=255)
    fcm_token: Optional[str] = None


class PairingVerifyResponse(BaseModel):
    device_id: str
    device_token: str  # Permanent device bearer token
    child_id: str
    child_name: str
    paired_at: datetime
    server_time: datetime

