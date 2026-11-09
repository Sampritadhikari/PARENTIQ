# PARENTIQ REST API & Real-Time Protocol Specification

The PARENTIQ backend exposes a modern, high-performance RESTful API adhering to the OpenAPI 3.1 specification, supplemented by real-time WebSocket multiplexing for sub-second telemetry and alerts.

- **Base URL (Production):** `https://api.parentiq.io/api/v1`
- **Base URL (Local Development):** `http://localhost:8000/api/v1` (or `http://10.0.2.2:8000/api/v1` from Android Emulator)
- **Interactive Swagger Documentation:** `http://localhost:8000/docs`
- **ReDoc Technical Schema:** `http://localhost:8000/redoc`

---

## 1. Authentication & Security Headers

All protected endpoints require a valid JSON Web Token (JWT) in the HTTP Authorization header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

### Response Status Codes:
- `200 OK`: Successful synchronous operation.
- `201 Created`: Resource successfully provisioned.
- `400 Bad Request`: Validation failure or business logic violation.
- `401 Unauthorized`: Missing, expired, or malformed authentication token.
- `403 Forbidden`: Insufficient role permissions or unauthorized child profile access.
- `404 Not Found`: Resource does not exist.
- `422 Unprocessable Entity`: Schema payload validation failure.
- `500 Internal Server Error`: Unhandled server exception.

---

## 2. API Endpoints Reference

### 2.1 Authentication (`/api/v1/auth`)

#### `POST /auth/register`
Creates a new parent guardian account.
- **Request Body:**
  ```json
  {
    "email": "guardian@example.com",
    "password": "StrongPassword123!",
    "full_name": "Sarah Connor",
    "phone_number": "+15551234567"
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "id": "u_948a27d1-cf1b-4d6f",
    "email": "guardian@example.com",
    "full_name": "Sarah Connor",
    "role": "PARENT",
    "created_at": "2026-11-07T10:00:00Z"
  }
  ```

#### `POST /auth/login`
Authenticates credentials and returns access and refresh tokens.
- **Request Body:** Form-urlencoded or JSON:
  ```json
  {
    "username": "guardian@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "8f9a2b...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": { ... }
  }
  ```

---

### 2.2 Device Pairing (`/api/v1/pairing`)

#### `POST /pairing/generate-code` (Parent Protected)
Generates an expiring 6-digit one-time code for child device enrollment.
- **Request Body:**
  ```json
  {
    "child_id": "c_58e2a1b9-3d1f"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "pairing_code": "PQ7K9A",
    "expires_at": "2026-11-07T10:15:00Z",
    "expires_in_seconds": 900
  }
  ```

#### `POST /pairing/verify` (Public / Child Onboarding)
Verifies the pairing code and provisions permanent child device credentials.
- **Request Body:**
  ```json
  {
    "pairing_code": "PQ7K9A",
    "device_name": "Liam's Galaxy S23",
    "device_model": "SM-S911B",
    "os_version": "Android 14 (API 34)",
    "app_version": "1.0.0",
    "device_fingerprint": "f8d3a17e-49c0-4e4b",
    "fcm_token": "fcm_token_string..."
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "device_id": "d_12c3e4f5-6789",
    "device_token": "eyJhbGciOi...",
    "child_id": "c_58e2a1b9-3d1f",
    "child_name": "Liam Connor"
  }
  ```

---

### 2.3 Device Telemetry & Heartbeat (`/api/v1/devices`)

#### `POST /devices/heartbeat` (Child Protected)
Transmits periodic battery, network status, and permission health states.
- **Request Body:**
  ```json
  {
    "battery_level": 84,
    "is_charging": false,
    "network_type": "WIFI",
    "permissions": {
      "has_location_permission": true,
      "has_background_location": true,
      "has_usage_stats": true,
      "has_accessibility": true,
      "has_notification_listener": true,
      "has_overlay_permission": true,
      "has_battery_optimization_ignored": true,
      "has_media_projection": false
    }
  }
  ```

---

### 2.4 Location & Geofencing (`/api/v1/location`)

#### `POST /location/batch` (Child Protected)
Transmits GPS location batches from `LocationTrackingService`.
- **Request Body:**
  ```json
  {
    "locations": [
      {
        "latitude": 37.774929,
        "longitude": -122.419416,
        "accuracy": 8.5,
        "speed": 1.2,
        "battery_level": 84,
        "provider": "fused",
        "address": "Market St, San Francisco, CA"
      }
    ]
  }
  ```

#### `GET /location/latest/{device_id}` (Parent Protected)
Returns the most recent GPS fix for a child device.

#### `POST /location/geofences` (Parent Protected)
Creates a new circular geofence boundary.
- **Request Body:**
  ```json
  {
    "child_id": "c_58e2a1b9-3d1f",
    "name": "Lincoln Middle School",
    "latitude": 37.7833,
    "longitude": -122.4167,
    "radius_meters": 200.0,
    "alert_on_entry": true,
    "alert_on_exit": true
  }
  ```

---

### 2.5 Screen Time Management (`/api/v1/screentime`)

#### `GET /screentime/rules/{child_id}` & `PATCH /screentime/rules/{child_id}`
Retrieves or updates screen time allotments and schedule locks.
- **Request Body (PATCH):**
  ```json
  {
    "daily_limit_minutes": 150,
    "bedtime_start": "21:30",
    "bedtime_end": "07:00",
    "school_mode_enabled": true,
    "is_instant_locked": false
  }
  ```

#### `POST /screentime/bonus-request` (Child Protected)
Child requests extra minutes.
- **Request Body:**
  ```json
  {
    "minutes_requested": 30,
    "reason": "Completing history assignment project"
  }
  ```

---

### 2.6 Application Management (`/api/v1/apps`)

#### `POST /apps/inventory` (Child Protected)
Uploads installed application catalog.

#### `POST /apps/restrictions` (Parent Protected)
Sets individual application blocks or daily quotas.
- **Request Body:**
  ```json
  {
    "device_id": "d_12c3e4f5-6789",
    "package_name": "com.zhiliaoapp.musically",
    "is_blocked": true,
    "daily_limit_minutes": 45
  }
  ```

---

### 2.7 Online Safety & Emergency Alerts (`/api/v1/safety`)

#### `POST /safety/sos` (Child Protected)
Triggers high-priority emergency SOS dispatch broadcasted across WebSockets and SMS/push notifications.

#### `POST /safety/inspect-url` (Child Protected)
Evaluates browser domain against categories (Adult, Gambling, Phishing, Violence).

#### `POST /safety/inspect-content` (Child Protected)
Scans message notification snippets for harassment, cyberbullying, or self-harm keywords.

---

### 2.8 Disclosed Live Monitoring (`/api/v1/monitoring`)

#### `POST /monitoring/session/initiate` (Parent Protected)
Initiates a transparent live screen sharing request.

#### `POST /monitoring/session/{id}/respond` (Child Protected)
Child grants or declines explicit consent:
```json
{
  "child_consent_granted": true
}
```

#### `POST /monitoring/session/{id}/terminate`
Terminates stream and revokes virtual display projection.

---

## 3. Real-Time WebSockets (`/ws`)

### 3.1 Parent Stream (`/ws/parent/{parent_id}`)
- Subscribes to live location updates, geofence enter/exit events, battery warnings, and SOS dispatches.
- Message format:
  ```json
  {
    "event": "LOCATION_UPDATE",
    "child_id": "c_58e2a1b9-3d1f",
    "latitude": 37.774929,
    "longitude": -122.419416,
    "accuracy": 8.5,
    "battery_level": 84,
    "timestamp": "2026-11-07T10:14:22Z"
  }
  ```

### 3.2 Child Stream (`/ws/device/{device_id}`)
- Receives immediate parent commands: Instant Device Lock, Rule Updates, and Screen Share Session Requests.

