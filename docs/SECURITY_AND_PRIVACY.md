# PARENTIQ Security, Privacy, and Ethical Oversight Framework

## 1. Ethical Statement: Protecting Children Without Covert Spyware

The fundamental tenet of PARENTIQ is that **safety does not require deception**. Legacy surveillance tools (often classified as "stalkerware") operate covertly, disguising icons, bypassing user consent, and recording private credentials. This breaks family trust, violates user dignity, and introduces massive cybersecurity vulnerabilities.

PARENTIQ is engineered from the ground up as a **transparent safety companion**:
1. **Visible Identity:** The app displays an unhidden icon in the child device's app drawer labeled `PARENTIQ Child`.
2. **Persistent Awareness:** An unremovable notification is displayed whenever background location tracking or screen sharing is active.
3. **No Secret Audio/Video:** The camera and microphone are **never** secretly turned on. Live screen sharing requires per-session confirmation and displays an unmistakable ongoing notification.
4. **No Keylogging:** Keystrokes, passwords, private chats, and credit card numbers are never intercepted or recorded.
5. **Child Empowerment:** The child has a dedicated status screen displaying their daily limits, a one-tap Emergency SOS button, and an in-app system to request bonus screen time.

---

## 2. Regulatory & Platform Compliance

### 2.1 Google Play Store Policy Compliance
- **Accessibility Service Declaration:** Used strictly in accordance with Google Play's accessibility guidelines for legitimate parental control (inspecting browser URL address bars to block adult content and displaying an overlay when an app limit expires).
- **Foreground Service Transparency:** Every background operation (Location, MediaProjection) declares an appropriate `foregroundServiceType` and presents a user-facing notification with category `CATEGORY_SERVICE`.
- **MediaProjection Consent:** The app invokes the official system `MediaProjectionManager.createScreenCaptureIntent()` dialog, ensuring the child is explicitly presented with Android's system warning before any frame capture begins.

### 2.2 Global Child Privacy Laws
- **COPPA (United States):** Ensures parental consent is established during pairing before any child telemetry is ingested.
- **GDPR-K (European Union):** Adheres to data minimization principles. Location trails expire after 30 days, sensitive records are encrypted at rest, and parents have full self-service rights to export or delete all associated child data.

---

## 3. Cryptography & Security Measures

### 3.1 Encryption at Rest & Mobile Storage
- **Android KeyStore & EncryptedSharedPreferences:** The child companion stores its device token and pairing configuration using AES-256 GCM encryption keyed by the hardware-backed Android KeyStore.
- **Database Encryption:** Sensitive data (audit logs, user emails, parent contact numbers) are stored using encrypted fields and parameterized relational tables.

### 3.2 Transport Security
- **Strict HTTPS / TLS 1.3:** All HTTP traffic is transmitted over HTTPS with forward secrecy.
- **Secure WebSockets (WSS):** WebSocket connections use encrypted TLS tunnels with per-connection authentication handshake.

### 3.3 Authentication & Authorization
- **HMAC-SHA256 JWTs:** Access tokens are signed using high-entropy secrets and have an expiry of 30 minutes.
- **Refresh Token Rotation:** Refresh tokens are single-use; issuing a new access token invalidates the previous refresh token to prevent replay attacks.
- **Role-Based Access Control (RBAC):** Backend endpoints verify ownership relationships; parents cannot query devices or children that belong to other family units.
- **Bcrypt Password Hashing:** User passwords are encrypted using standard 12-round bcrypt with strict input sanitization.

---

## 4. Emergency & Incident Response

### 4.1 Emergency SOS Dispatch Protocol
When a child taps the Emergency SOS button:
1. High-precision GPS coordinates are immediately acquired.
2. An urgent payload is transmitted over REST and WebSockets simultaneously.
3. The parent receives an override push notification and visual alarm banner across all active devices.
4. An immutable emergency incident is recorded in `safety_alerts` with severity `EMERGENCY`.

### 4.2 Anti-Tamper & Health Audits
If a child attempts to disable the Accessibility Service or revoke permissions, `HeartbeatWorker` reports a permissions degradation within 15 minutes, alerting the parent with instructions on how to discuss and re-enable protection.

