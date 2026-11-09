# PARENTIQ Firebase Cloud Messaging (FCM) Setup Guide

PARENTIQ utilizes Firebase Cloud Messaging (FCM) to deliver sub-second push notifications to parent devices and to dispatch silent control commands to child companion devices.

---

## 1. Firebase Project Setup

1. Open the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add Project** and name it `PARENTIQ-Platform` (or your preferred name).
3. Disable Google Analytics (optional, for minimal telemetry) or enable if desired.
4. Once created, navigate to **Project Settings** (gear icon) -> **Service Accounts**.

---

## 2. Backend Service Account Configuration

The FastAPI backend uses the Firebase Admin SDK to dispatch notifications to devices:

1. In **Project Settings** -> **Service Accounts**, click **Generate New Private Key**.
2. Save the downloaded JSON file securely (e.g., as `backend/firebase-service-account.json`).
3. Set the file path in your `backend/.env` file:
   ```ini
   FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
   ```
4. **Security Note:** Never commit `firebase-service-account.json` to version control. It is ignored in `.gitignore`.

---

## 3. Child Android Companion Setup

1. In the Firebase Console, click **Add App** and select **Android**.
2. Register the application:
   - **Android package name:** `com.parentiq.child`
   - **App nickname:** `PARENTIQ Child`
3. Download the generated `google-services.json` file.
4. Copy `google-services.json` into:
   ```text
   child_app/app/google-services.json
   ```
5. The Google Services Gradle plugin is already pre-configured in `child_app/build.gradle.kts` and `child_app/app/build.gradle.kts`.

---

## 4. Parent Flutter Application Setup

1. In the Firebase Console, click **Add App** and register both Android and iOS:
   - **Android package name:** `com.parentiq.parent`
   - **iOS bundle ID:** `com.parentiq.parent`
2. Download `google-services.json` and place it in:
   ```text
   parent_app/android/app/google-services.json
   ```
3. For iOS, download `GoogleService-Info.plist` and place it in:
   ```text
   parent_app/ios/Runner/GoogleService-Info.plist
   ```

---

## 5. Notification Message Payloads

### High-Priority Emergency SOS Alert
```json
{
  "message": {
    "token": "<PARENT_FCM_TOKEN>",
    "notification": {
      "title": "🚨 EMERGENCY SOS: Liam Connor",
      "body": "Liam triggered an Emergency SOS near Market St. Tap to view live location."
    },
    "data": {
      "category": "SAFETY",
      "alert_type": "SOS",
      "child_id": "c_58e2a1b9-3d1f",
      "latitude": "37.774929",
      "longitude": "-122.419416"
    },
    "android": {
      "priority": "high",
      "notification": {
        "channel_id": "parentiq_safety_channel",
        "sound": "emergency_alarm"
      }
    }
  }
}
```

### Silent Policy Sync Command to Child Device
```json
{
  "message": {
    "token": "<CHILD_FCM_TOKEN>",
    "data": {
      "action": "SYNC_RULES",
      "instant_lock": "true",
      "daily_limit_minutes": "120"
    },
    "android": {
      "priority": "high"
    }
  }
}
```

