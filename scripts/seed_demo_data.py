"""
PARENTIQ Realistic Demo Data Seeder.
Populates the database with parents, children, paired devices, location history,
geofences, app usage, screen time rules, and safety alerts.
"""
import sys
import os
from datetime import datetime, date, timedelta, timezone
import uuid

# Ensure backend path is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.parent import ParentProfile
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.pairing import DevicePairing, DevicePermission
from app.models.location import LocationHistory, Geofence
from app.models.screentime import ScreenTimeRule, ScreenTimeLog
from app.models.app_usage import InstalledApp, AppUsage, AppRestriction
from app.models.safety import SafetyAlert, Notification

def seed_database():
    db = SessionLocal()
    print("Seeding PARENTIQ Database with Demo Data...")

    try:
        # Check if parent user already exists
        demo_email = "parent@parentiq.com"
        user = db.query(User).filter(User.email == demo_email).first()
        if user:
            print(f"Demo parent '{demo_email}' already exists. Skipping seed.")
            return

        # 1. Create Demo Parent User
        user = User(
            id=str(uuid.uuid4()),
            email=demo_email,
            hashed_password=get_password_hash("Password123!"),
            full_name="Sarah Connor",
            phone_number="+1 555-019-2834",
            role="parent",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.flush()

        # 2. Parent Profile
        parent_profile = ParentProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            pin_hash=get_password_hash("1234"),
            notification_preferences={
                "location_alerts": True,
                "geofence_alerts": True,
                "screentime_alerts": True,
                "app_install_alerts": True,
                "safety_keyword_alerts": True,
                "battery_alerts": True,
                "device_offline_alerts": True,
            },
            created_at=datetime.now(timezone.utc)
        )
        db.add(parent_profile)
        db.flush()

        # 3. Child Profiles
        child_liam = ChildProfile(
            id=str(uuid.uuid4()),
            parent_id=parent_profile.id,
            name="Liam Connor",
            age=12,
            gender="Male",
            avatar_url="https://images.unsplash.com/photo-1544717305-2782549b5136?w=150",
            created_at=datetime.now(timezone.utc)
        )
        child_emma = ChildProfile(
            id=str(uuid.uuid4()),
            parent_id=parent_profile.id,
            name="Emma Connor",
            age=8,
            gender="Female",
            avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150",
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([child_liam, child_emma])
        db.flush()

        # 4. Devices
        dev_liam = Device(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            device_name="Liam's Galaxy S23",
            device_model="Samsung Galaxy S23 (SM-S911B)",
            os_version="Android 14",
            app_version="1.0.0",
            device_fingerprint=f"fp_samsung_{uuid.uuid4().hex[:12]}",
            battery_level=86,
            is_charging=False,
            network_type="wifi",
            is_online=True,
            last_seen_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        dev_emma = Device(
            id=str(uuid.uuid4()),
            child_id=child_emma.id,
            device_name="Emma's Pixel 7a",
            device_model="Google Pixel 7a",
            os_version="Android 14",
            app_version="1.0.0",
            device_fingerprint=f"fp_pixel_{uuid.uuid4().hex[:12]}",
            battery_level=64,
            is_charging=True,
            network_type="cellular",
            is_online=True,
            last_seen_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([dev_liam, dev_emma])
        db.flush()

        # 4b. Active Device Pairings
        pairing_liam = DevicePairing(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            pairing_code="PQ8K4X",
            device_token="demo_device_token_liam_s23",
            is_used=True,
            attempts=1,
            paired_device_id=dev_liam.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            created_at=datetime.now(timezone.utc)
        )
        pairing_emma = DevicePairing(
            id=str(uuid.uuid4()),
            child_id=child_emma.id,
            pairing_code="PQ2M9Z",
            device_token="demo_device_token_emma_p7a",
            is_used=True,
            attempts=1,
            paired_device_id=dev_emma.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([pairing_liam, pairing_emma])
        db.flush()

        # 5. Device Permissions Health
        perm_liam = DevicePermission(
            id=str(uuid.uuid4()),
            device_id=dev_liam.id,
            has_location_permission=True,
            has_background_location=True,
            has_usage_stats=True,
            has_accessibility=True,
            has_notification_listener=True,
            has_overlay_permission=True,
            has_battery_optimization_ignored=True,
            has_media_projection=False,
            updated_at=datetime.now(timezone.utc)
        )
        perm_emma = DevicePermission(
            id=str(uuid.uuid4()),
            device_id=dev_emma.id,
            has_location_permission=True,
            has_background_location=True,
            has_usage_stats=True,
            has_accessibility=True,
            has_notification_listener=True,
            has_overlay_permission=True,
            has_battery_optimization_ignored=True,
            has_media_projection=False,
            updated_at=datetime.now(timezone.utc)
        )
        db.add_all([perm_liam, perm_emma])

        # 6. Screen Time Rules
        rule_liam = ScreenTimeRule(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            daily_limit_minutes=120,
            bedtime_mode_enabled=True,
            bedtime_start="21:00",
            bedtime_end="07:00",
            school_mode_enabled=True,
            school_mode_start="08:30",
            school_mode_end="15:30",
            instant_lock=False,
            created_at=datetime.now(timezone.utc)
        )
        rule_emma = ScreenTimeRule(
            id=str(uuid.uuid4()),
            child_id=child_emma.id,
            daily_limit_minutes=60,
            bedtime_mode_enabled=True,
            bedtime_start="20:00",
            bedtime_end="07:30",
            school_mode_enabled=False,
            instant_lock=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([rule_liam, rule_emma])

        # 7. Screen Time Daily Logs
        today_date = date.today()
        log_liam = ScreenTimeLog(
            id=str(uuid.uuid4()),
            device_id=dev_liam.id,
            log_date=today_date,
            total_screen_time_seconds=5400, # 90 minutes
            unlock_count=14,
            extra_time_granted_minutes=15,
            bonus_requests_pending=0
        )
        db.add(log_liam)

        # 8. Geofences
        gf_home = Geofence(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            name="Home (Market St)",
            latitude=37.774929,
            longitude=-122.419416,
            radius_meters=150.0,
            zone_type="home",
            notify_on_entry=True,
            notify_on_exit=True,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        gf_school = Geofence(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            name="Lincoln Middle School",
            latitude=37.783300,
            longitude=-122.416700,
            radius_meters=200.0,
            zone_type="school",
            notify_on_entry=True,
            notify_on_exit=True,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([gf_home, gf_school])

        # 9. Location History (Trail of points)
        base_lat, base_lng = 37.774929, -122.419416
        for i in range(10):
            pt = LocationHistory(
                id=str(uuid.uuid4()),
                device_id=dev_liam.id,
                latitude=base_lat + (i * 0.0008),
                longitude=base_lng + (i * 0.0005),
                accuracy=6.5,
                speed=1.5,
                battery_level=86 - (i // 2),
                provider="fused",
                address=f"Near {1000 + i*50} Market St, San Francisco, CA",
                recorded_at=datetime.now(timezone.utc) - timedelta(minutes=(10 - i) * 15),
                created_at=datetime.now(timezone.utc)
            )
            db.add(pt)

        # 10. Installed Apps & Usage for Liam
        apps_data = [
            ("com.roblox.client", "Roblox", "Games", 2520, 3, False),
            ("com.google.android.youtube", "YouTube", "Entertainment", 1800, 4, False),
            ("com.duolingo", "Duolingo", "Education", 1200, 2, False),
            ("com.whatsapp", "WhatsApp", "Communication", 600, 8, False),
            ("com.android.chrome", "Google Chrome", "Browsers", 450, 5, True),
            ("com.zhiliaoapp.musically", "TikTok", "Social Media", 0, 0, False)
        ]

        for pkg, name, cat, sec, launches, is_sys in apps_data:
            installed = InstalledApp(
                id=str(uuid.uuid4()),
                device_id=dev_liam.id,
                package_name=pkg,
                app_name=name,
                version_name="3.2.1",
                category=cat,
                is_system_app=is_sys,
                installed_at=datetime.now(timezone.utc)
            )
            db.add(installed)

            if sec > 0:
                usage = AppUsage(
                    id=str(uuid.uuid4()),
                    device_id=dev_liam.id,
                    package_name=pkg,
                    app_name=name,
                    category=cat,
                    usage_date=today_date,
                    foreground_time_seconds=sec,
                    launch_count=launches,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(usage)

        # 11. App Restrictions
        restrict_tiktok = AppRestriction(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            package_name="com.zhiliaoapp.musically",
            app_name="TikTok",
            is_blocked=True,
            daily_limit_minutes=0,
            created_at=datetime.now(timezone.utc)
        )
        restrict_roblox = AppRestriction(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            package_name="com.roblox.client",
            app_name="Roblox",
            is_blocked=False,
            daily_limit_minutes=45,
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([restrict_tiktok, restrict_roblox])

        # 12. Safety Alerts
        alert1 = SafetyAlert(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            device_id=dev_liam.id,
            alert_type="inappropriate_web",
            severity="warning",
            title="Inappropriate Adult Domain Blocked",
            description="Attempted access to 'adult-content-sample.com' blocked in Google Chrome by PARENTIQ Safety Guard.",
            source_app="com.android.chrome",
            url="https://adult-content-sample.com",
            is_reviewed=False,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        alert2 = SafetyAlert(
            id=str(uuid.uuid4()),
            child_id=child_liam.id,
            device_id=dev_liam.id,
            alert_type="geofence_exit",
            severity="info",
            title="Geofence Exit: Lincoln Middle School",
            description="Liam departed Lincoln Middle School safe zone at 15:32.",
            source_app="LocationTrackingService",
            is_reviewed=True,
            created_at=datetime.now(timezone.utc) - timedelta(hours=4)
        )
        db.add_all([alert1, alert2])

        # 13. System Notifications
        notif1 = Notification(
            id=str(uuid.uuid4()),
            user_id=user.id,
            device_id=dev_liam.id,
            category="safety",
            title="Safety Guard Blocked Dangerous Site",
            body="Liam attempted to access an adult website. The request was blocked immediately.",
            payload={"alert_id": alert1.id, "child_id": child_liam.id},
            is_read=False,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        notif2 = Notification(
            id=str(uuid.uuid4()),
            user_id=user.id,
            device_id=dev_liam.id,
            category="location",
            title="Liam arrived at Lincoln Middle School",
            body="Liam safely entered the school geofence at 08:28 AM.",
            payload={"child_id": child_liam.id},
            is_read=True,
            created_at=datetime.now(timezone.utc) - timedelta(hours=7)
        )
        db.add_all([notif1, notif2])

        db.commit()
        print("\nSUCCESS! PARENTIQ Demo Data Seeded:")
        print(f"Parent Login: {demo_email} | Password: Password123!")
        print(f"Children: Liam Connor (12), Emma Connor (8)")
        print(f"Devices: Liam's Galaxy S23 (Online, 86%), Emma's Pixel 7a (Online, 64%)")
        print(f"Geofences: Home, Lincoln Middle School")
        print(f"App Inventory: Roblox, YouTube, Duolingo, WhatsApp, Chrome, TikTok (Blocked)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
