# Import all models so that Base has them before being imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.parent import ParentProfile  # noqa
from app.models.child import ChildProfile  # noqa
from app.models.device import Device  # noqa
from app.models.pairing import DevicePairing, DevicePermission  # noqa
from app.models.location import LocationHistory, Geofence  # noqa
from app.models.screentime import ScreenTimeRule, ScreenTimeLog  # noqa
from app.models.app_usage import InstalledApp, AppUsage, AppRestriction  # noqa
from app.models.safety import SafetyAlert, Notification  # noqa
from app.models.monitoring import LiveSession, ActivityReport, AuditLog  # noqa

