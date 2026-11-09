"""
PARENTIQ Child Telemetry Simulator.
Simulates a real Android child companion device:
- Authenticates or retrieves device token
- Streams moving GPS coordinates along a realistic route
- Sends periodic heartbeats with battery status
- Can trigger an emergency SOS alert
"""
import sys
import os
import time
import requests
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Waypoints along Market St towards Lincoln Middle School in San Francisco
WAYPOINTS = [
    {"lat": 37.774929, "lng": -122.419416, "addr": "1000 Market St, San Francisco, CA"},
    {"lat": 37.776100, "lng": -122.418700, "addr": "1050 Market St, San Francisco, CA"},
    {"lat": 37.777400, "lng": -122.417900, "addr": "1120 Market St, San Francisco, CA"},
    {"lat": 37.779000, "lng": -122.417200, "addr": "1200 Market St, San Francisco, CA"},
    {"lat": 37.781200, "lng": -122.416800, "addr": "Near City Hall, San Francisco, CA"},
    {"lat": 37.783300, "lng": -122.416700, "addr": "Lincoln Middle School, San Francisco, CA"}
]

def simulate_device(num_steps=6, interval_sec=3):
    print("==================================================")
    print("   PARENTIQ Child Companion Telemetry Simulator   ")
    print("==================================================")

    # 1. Login as parent to retrieve device info
    print("\n[1/3] Authenticating with PARENTIQ Backend...")
    try:
        login_res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "parent@parentiq.com",
            "password": "Password123!"
        }, timeout=5)
    except Exception as e:
        print(f"Failed to connect to backend at {BASE_URL}: {e}")
        return

    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return

    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Children and Devices
    print("[2/3] Fetching child profile and device ID...")
    children_res = requests.get(f"{BASE_URL}/children/", headers=headers)
    children = children_res.json()
    if not children:
        print("No children found. Please run seed_demo_data.py first.")
        return

    liam = next((c for c in children if "Liam" in c["name"]), children[0])
    child_id = liam["id"]

    devices = liam.get("devices", [])
    if not devices:
        # Fallback to GET endpoint
        devices_res = requests.get(f"{BASE_URL}/children/{child_id}/devices", headers=headers)
        if devices_res.status_code == 200 and isinstance(devices_res.json(), list):
            devices = devices_res.json()

    if not devices:
        print("No devices found for child.")
        return

    device = devices[0]
    device_id = device["id"]
    print(f"Target Child: {liam['name']} (ID: {child_id})")
    print(f"Target Device: {device['device_name']} (ID: {device_id})")

    # Companion device bearer token
    device_headers = {"Authorization": "Bearer demo_device_token_liam_s23"}

    # 3. Simulate Telemetry Stream
    print(f"\n[3/3] Streaming {num_steps} GPS Waypoints & Heartbeats (interval: {interval_sec}s)...")
    battery = 86

    for idx, wp in enumerate(WAYPOINTS[:num_steps]):
        battery -= random.choice([0, 1])

        # A. Send Heartbeat
        heartbeat_payload = {
            "battery_level": battery,
            "is_charging": False,
            "network_type": "WIFI" if idx < 3 else "CELLULAR",
            "permissions": {
                "has_location_permission": True,
                "has_background_location": True,
                "has_usage_stats": True,
                "has_accessibility": True,
                "has_notification_listener": True,
                "has_overlay_permission": True,
                "has_battery_optimization_ignored": True,
                "has_media_projection": False
            }
        }
        hb_res = requests.post(f"{BASE_URL}/devices/heartbeat", json=heartbeat_payload, headers=device_headers)

        # B. Send Location Batch
        location_payload = {
            "locations": [
                {
                    "latitude": wp["lat"],
                    "longitude": wp["lng"],
                    "accuracy": 5.2,
                    "speed": 1.4,
                    "battery_level": battery,
                    "provider": "fused",
                    "address": wp["addr"]
                }
            ]
        }
        loc_res = requests.post(f"{BASE_URL}/location/batch", json=location_payload, headers=device_headers)

        print(f"[{idx+1}/{num_steps}] GPS Fix: ({wp['lat']:.6f}, {wp['lng']:.6f}) | Battery: {battery}% | Address: {wp['addr']}")

        if idx < num_steps - 1:
            time.sleep(interval_sec)

    print("\nTelemetry simulation completed successfully!")
    print("Refresh your Web Dashboard at http://localhost:8000/dashboard to see updated coordinates!")

if __name__ == "__main__":
    simulate_device()

