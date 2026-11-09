# PARENTIQ Production Deployment & Infrastructure Guide

This guide details the complete deployment lifecycle for the PARENTIQ platform across containerized cloud infrastructure, PostgreSQL databases, reverse proxies, and mobile application releases.

---

## 1. Containerized Infrastructure (Docker Compose)

The easiest and most resilient method for deploying PARENTIQ is via Docker Compose, which orchestrates the FastAPI application, PostgreSQL 15, and Redis.

### 1.1 `docker-compose.yml`
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: parentiq_postgres
    restart: always
    environment:
      POSTGRES_DB: parentiq
      POSTGRES_USER: parentiq_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-SuperSecretPassword123!}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U parentiq_admin -d parentiq"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: parentiq_redis
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-RedisSecret123!}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: parentiq_backend
    restart: always
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      DATABASE_URL: postgresql+psycopg2://parentiq_admin:${POSTGRES_PASSWORD:-SuperSecretPassword123!}@db:5432/parentiq
      REDIS_URL: redis://:${REDIS_PASSWORD:-RedisSecret123!}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 30
      CORS_ORIGINS: "*"
    ports:
      - "8000:8000"
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"

volumes:
  postgres_data:
  redis_data:
```

### 1.2 `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 2. NGINX Reverse Proxy & WebSocket Configuration

For production HTTPS and WebSocket stream termination, place NGINX in front of the backend container:

```nginx
server {
    listen 80;
    server_name api.parentiq.io;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.parentiq.io;

    ssl_certificate /etc/letsencrypt/live/api.parentiq.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.parentiq.io/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Upgrade
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## 3. Database Migration Management

Apply database schema migrations using Alembic:

```bash
cd backend
# Run all pending migrations to bring the database to head
alembic upgrade head

# Roll back by one migration revision if necessary
alembic downgrade -1
```

---

## 4. Mobile Application Build Procedures

### 4.1 Parent Application (Flutter)
Compile production releases for Android and iOS:

```bash
cd parent_app

# Android App Bundle (AAB for Google Play)
flutter build appbundle --release

# Android Standalone APK
flutter build apk --release

# iOS Release
flutter build ipa --release
```

### 4.2 Child Companion Application (Android / Gradle)
Compile the standalone Android APK with Proguard minification enabled:

```bash
cd child_app

# Linux / macOS
./gradlew assembleRelease

# Windows PowerShell
.\gradlew.bat assembleRelease
```
The compiled APK will be generated at:
`child_app/app/build/outputs/apk/release/app-release.apk`

---

## 5. Health Checks & Telemetry

- **HTTP Liveness Probe:** `GET /health` returns `{"status": "ok"}`
- **System Metrics:** Ingest logs via Docker logging driver or ship to Datadog / Grafana Loki.

