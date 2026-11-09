import app.db.base  # Register all 17 models in SQLAlchemy registry
import pytest
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

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
    safety,
    screentime,
    settings,
)
from app.api.v1.endpoints.safety import ContentInspectionRequest, URLInspectionRequest
from app.db.session import SessionLocal
from app.models.child import ChildProfile
from app.models.device import Device
from app.models.parent import ParentProfile
from app.models.user import User
from app.schemas.apps import AppRestrictionUpdate, AppUsageBatch, AppUsageCreate, InstalledAppBatch, InstalledAppCreate
from app.schemas.auth import UserCreate, UserLogin
from app.schemas.child import ChildCreate, DeviceHeartbeat, DevicePermissionState
from app.schemas.location import GeofenceCreate, LocationBatchCreate, LocationLogCreate
from app.schemas.monitoring import LiveSessionConsent, LiveSessionRequest
from app.schemas.pairing import PairingVerifyRequest
from app.schemas.screentime import BonusTimeAction, BonusTimeRequest, ScreenTimeRuleUpdate, ScreenTimeSync


def run_sync(coro):
    """Executes an async endpoint coroutine synchronously without socketpair loopback locks."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture(scope="module")
def db() -> Session:
    session = SessionLocal()
    yield session
    session.close()


def test_auth_registration_and_login(db: Session):
    email = f"parent_{int(datetime.now().timestamp())}@parentiq.com"
    token_res = auth.register(
        user_in=UserCreate(
            email=email,
            password="SecurePassword123!",
            full_name="Sarah Connor",
            phone_number="+1555123456",
        ),
        db=db,
    )
    assert token_res["access_token"] is not None
    assert token_res["refresh_token"] is not None

    login_res = auth.login(
        login_in=UserLogin(email=email, password="SecurePassword123!"),
        db=db,
    )
    assert login_res["access_token"] is not None

    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.full_name == "Sarah Connor"


def test_child_profile_and_dashboard(db: Session):
    user = db.query(User).first()
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == user.id).first()

    child = children.create_child(
        child_in=ChildCreate(name="John Connor", age=10, gender="male"),
        parent=parent,
        db=db,
    )
    assert child.id is not None
    assert child.name == "John Connor"

    child_list = children.list_children(parent=parent, db=db)
    assert any(c.id == child.id for c in child_list)

    dash = children.get_child_dashboard(child_id=child.id, parent=parent, db=db)
    assert dash["child_name"] == "John Connor"
    assert dash["daily_limit_minutes"] == 120
    assert dash["today_screen_time_seconds"] == 0


def test_device_pairing_and_heartbeat(db: Session):
    user = db.query(User).first()
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == user.id).first()
    child = db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).first()

    init_res = pairing.initiate_pairing(child_id=child.id, parent=parent, db=db)
    assert len(init_res["pairing_code"]) == 6
    code = init_res["pairing_code"]

    fingerprint = f"FP_TEST_{child.id}_{int(datetime.now().timestamp())}"
    verify_res = pairing.verify_pairing(
        req=PairingVerifyRequest(
            pairing_code=code,
            device_name="Samsung Galaxy Tab",
            device_model="SM-T500",
            os_version="Android 13",
            app_version="1.0.0",
            device_fingerprint=fingerprint,
        ),
        db=db,
    )
    assert verify_res["device_token"] is not None
    device_id = verify_res["device_id"]

    device = db.query(Device).filter(Device.id == device_id).first()
    hb_res = devices.device_heartbeat(
        heartbeat=DeviceHeartbeat(
            battery_level=92,
            is_charging=True,
            network_type="wifi",
            permissions=DevicePermissionState(
                has_location_permission=True,
                has_background_location=True,
                has_usage_stats=True,
                has_accessibility=True,
                has_notification_listener=True,
                has_overlay_permission=True,
                has_battery_optimization_ignored=True,
                has_media_projection=False,
            ),
        ),
        device=device,
        db=db,
    )
    assert hb_res["status"] == "ok"
    assert device.battery_level == 92
    assert device.is_charging is True


def test_location_and_geofencing(db: Session):
    user = db.query(User).first()
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == user.id).first()
    child = db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).first()
    device = db.query(Device).filter(Device.child_id == child.id).first()

    gf = location.create_geofence(
        child_id=child.id,
        gf_in=GeofenceCreate(
            name="School Campus",
            zone_type="safe",
            latitude=37.7793,
            longitude=-122.4193,
            radius_meters=300.0,
            notify_on_entry=True,
            notify_on_exit=True,
        ),
        parent=parent,
        db=db,
    )
    assert gf.id is not None

    loc_res = run_sync(location.post_location_batch(
        batch=LocationBatchCreate(
            locations=[
                LocationLogCreate(
                    latitude=37.7794,
                    longitude=-122.4192,
                    accuracy=4.5,
                    speed=1.2,
                    battery_level=90,
                    provider="fused",
                    address="1 Dr Carlton B Goodlett Pl, San Francisco, CA",
                )
            ]
        ),
        device=device,
        db=db,
    ))
    assert loc_res["status"] == "recorded"

    curr = location.get_current_location(child_id=child.id, parent=parent, db=db)
    assert curr is not None
    assert abs(curr.latitude - 37.7794) < 0.001


def test_screentime_and_app_rules(db: Session):
    user = db.query(User).first()
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == user.id).first()
    child = db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).first()
    device = db.query(Device).filter(Device.child_id == child.id).first()

    updated_rules = run_sync(screentime.update_rules(
        child_id=child.id,
        update_in=ScreenTimeRuleUpdate(
            daily_limit_minutes=90,
            bedtime_mode_enabled=True,
            bedtime_start="21:30",
            bedtime_end="07:00",
            instant_lock=False,
        ),
        parent=parent,
        db=db,
    ))
    assert updated_rules.daily_limit_minutes == 90
    assert updated_rules.bedtime_mode_enabled is True

    st_sync = screentime.sync_screentime(
        sync_in=ScreenTimeSync(
            log_date=date.today(),
            total_screen_time_seconds=4200,
            unlock_count=22,
        ),
        device=device,
        db=db,
    )
    assert st_sync["status"] == "synced"

    req_res = run_sync(screentime.request_bonus_time(
        req=BonusTimeRequest(minutes_requested=30, reason="Finishing homework"),
        device=device,
        db=db,
    ))
    assert req_res["status"] == "request_delivered"

    action_res = run_sync(screentime.grant_bonus_time(
        child_id=child.id,
        action=BonusTimeAction(minutes_granted=30, approved=True),
        parent=parent,
        db=db,
    ))
    assert action_res["approved"] is True

    apps.sync_installed_apps(
        batch=InstalledAppBatch(
            apps=[
                InstalledAppCreate(package_name="com.roblox.client", app_name="Roblox", category="Games"),
                InstalledAppCreate(package_name="com.duolingo", app_name="Duolingo", category="Education"),
            ]
        ),
        device=device,
        db=db,
    )

    apps.sync_app_usage(
        batch=AppUsageBatch(
            usages=[
                AppUsageCreate(
                    package_name="com.roblox.client",
                    app_name="Roblox",
                    category="Games",
                    usage_date=date.today(),
                    foreground_time_seconds=2400,
                    launch_count=5,
                )
            ]
        ),
        device=device,
        db=db,
    )

    restr = run_sync(apps.set_app_restriction(
        child_id=child.id,
        restriction_in=AppRestrictionUpdate(
            package_name="com.roblox.client",
            app_name="Roblox",
            is_blocked=True,
            daily_limit_minutes=0,
            block_during_school=True,
            block_during_bedtime=True,
        ),
        parent=parent,
        db=db,
    ))
    assert restr.is_blocked is True


def test_safety_sos_and_live_monitoring(db: Session):
    user = db.query(User).first()
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == user.id).first()
    child = db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).first()
    device = db.query(Device).filter(Device.child_id == child.id).first()

    inspect_res = safety.inspect_url(
        req=URLInspectionRequest(url="https://free-casino-betting.com/play"),
        device=device,
        db=db,
    )
    assert inspect_res["blocked"] is True

    content_res = safety.inspect_content(
        req=ContentInspectionRequest(content="you are a loser go away", source_app="Discord"),
        device=device,
        db=db,
    )
    assert content_res["flagged"] is True

    sos_res = run_sync(safety.trigger_emergency_sos(device=device, db=db))
    assert sos_res["status"] == "sos_broadcasted"

    live_session = run_sync(monitoring.request_live_session(
        device_id=device.id,
        req=LiveSessionRequest(session_type="screen_mirror"),
        parent=parent,
        db=db,
    ))
    assert live_session.status == "requested"
    assert live_session.explicit_child_consent is False

    consent_res = run_sync(monitoring.submit_child_consent(
        consent=LiveSessionConsent(session_token=live_session.session_token, approved=True),
        device=device,
        db=db,
    ))
    assert consent_res["status"] == "active"

    term_res = run_sync(monitoring.terminate_live_session(session_id=live_session.id, db=db))
    assert term_res["status"] == "terminated"

    report = reports.get_activity_analytics(child_id=child.id, days=7, parent=parent, db=db)
    assert report["child_name"] == "John Connor"
    assert len(report["screen_time_trend"]) == 7
    assert report["total_safety_alerts"] >= 2
