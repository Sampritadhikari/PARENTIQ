import sqlite3
from app.db.base import Base

def test_database_tables():
    con = sqlite3.connect("parentiq.db")
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    con.close()
    
    expected_tables = [
        "users", "parent_profiles", "child_profiles", "devices",
        "device_pairings", "device_permissions", "location_history", "geofences",
        "screen_time_rules", "screen_time_logs", "installed_apps", "app_usage",
        "app_restrictions", "safety_alerts", "notifications", "live_sessions",
        "activity_reports", "audit_logs", "alembic_version"
    ]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' not found in database!"

