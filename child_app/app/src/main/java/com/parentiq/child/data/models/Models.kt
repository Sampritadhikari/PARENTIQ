package com.parentiq.child.data.models

import com.google.gson.annotations.SerializedName

data class PairingRequest(
    @SerializedName("pairing_code") val pairingCode: String,
    @SerializedName("device_name") val deviceName: String,
    @SerializedName("device_model") val deviceModel: String?,
    @SerializedName("os_version") val osVersion: String?,
    @SerializedName("app_version") val appVersion: String?,
    @SerializedName("device_fingerprint") val deviceFingerprint: String,
    @SerializedName("fcm_token") val fcmToken: String? = null
)

data class PairingResponse(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("device_token") val deviceToken: String,
    @SerializedName("child_id") val childId: String,
    @SerializedName("child_name") val childName: String
)

data class PermissionState(
    @SerializedName("has_location_permission") val hasLocationPermission: Boolean,
    @SerializedName("has_background_location") val hasBackgroundLocation: Boolean,
    @SerializedName("has_usage_stats") val hasUsageStats: Boolean,
    @SerializedName("has_accessibility") val hasAccessibility: Boolean,
    @SerializedName("has_notification_listener") val hasNotificationListener: Boolean,
    @SerializedName("has_overlay_permission") val hasOverlayPermission: Boolean,
    @SerializedName("has_battery_optimization_ignored") val hasBatteryOptimizationIgnored: Boolean,
    @SerializedName("has_media_projection") val hasMediaProjection: Boolean = false
)

data class HeartbeatRequest(
    @SerializedName("battery_level") val batteryLevel: Int,
    @SerializedName("is_charging") val isCharging: Boolean,
    @SerializedName("network_type") val networkType: String,
    @SerializedName("permissions") val permissions: PermissionState
)

data class LocationBatch(
    @SerializedName("locations") val locations: List<LocationItem>
)

data class LocationItem(
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("accuracy") val accuracy: Float?,
    @SerializedName("speed") val speed: Float?,
    @SerializedName("battery_level") val batteryLevel: Int?,
    @SerializedName("provider") val provider: String = "fused",
    @SerializedName("address") val address: String? = null
)

data class InstalledAppItem(
    @SerializedName("package_name") val packageName: String,
    @SerializedName("app_name") val appName: String,
    @SerializedName("version_name") val versionName: String?,
    @SerializedName("category") val category: String = "Other",
    @SerializedName("is_system_app") val isSystemApp: Boolean = false
)

data class InstalledAppBatch(
    @SerializedName("apps") val apps: List<InstalledAppItem>
)

data class AppUsageItem(
    @SerializedName("package_name") val packageName: String,
    @SerializedName("app_name") val appName: String,
    @SerializedName("category") val category: String,
    @SerializedName("usage_date") val usageDate: String,
    @SerializedName("foreground_time_seconds") val foregroundTimeSeconds: Int,
    @SerializedName("launch_count") val launchCount: Int
)

data class AppUsageBatch(
    @SerializedName("usages") val usages: List<AppUsageItem>
)

data class ScreenTimeSyncRequest(
    @SerializedName("log_date") val logDate: String,
    @SerializedName("total_screen_time_seconds") val totalScreenTimeSeconds: Int,
    @SerializedName("unlock_count") val unlockCount: Int
)

data class BonusTimeRequest(
    @SerializedName("minutes_requested") val minutesRequested: Int,
    @SerializedName("reason") val reason: String?
)

data class URLInspectionRequest(
    @SerializedName("url") val url: String,
    @SerializedName("source_app") val sourceApp: String = "Browser"
)

data class ContentInspectionRequest(
    @SerializedName("content") val content: String,
    @SerializedName("source_app") val sourceApp: String
)

