package com.parentiq.child.services

import android.Manifest
import android.app.AppOpsManager
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.os.PowerManager
import android.os.Process
import android.provider.Settings
import android.util.Log
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.parentiq.child.data.api.ApiClient
import com.parentiq.child.data.models.*
import com.parentiq.child.data.storage.DevicePreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale

class HeartbeatWorker(
    private val context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val TAG = "HeartbeatWorker"
    }

    private val apiClient = ApiClient(context)
    private val prefs = DevicePreferences(context)

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        if (!prefs.isPaired) {
            Log.d(TAG, "Device not paired yet. Skipping heartbeat.")
            return@withContext Result.success()
        }

        try {
            // 1. Collect Battery info
            val batteryStatus = getBatteryInfo()

            // 2. Collect Network Type
            val networkType = getNetworkType()

            // 3. Collect Permission Health
            val permissions = checkPermissionsHealth()

            // 4. Send Heartbeat to Backend
            val heartbeat = HeartbeatRequest(
                batteryLevel = batteryStatus.first,
                isCharging = batteryStatus.second,
                networkType = networkType,
                permissions = permissions
            )

            val success = apiClient.sendHeartbeat(heartbeat)
            Log.d(TAG, "Heartbeat sent: success=$success, battery=${heartbeat.batteryLevel}%, net=$networkType")

            // 5. If usage stats permission is granted, collect and sync app usage
            if (permissions.hasUsageStats) {
                syncAppUsageData()
            }

            // 6. Sync installed applications periodically
            syncInstalledApps()

            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "Error executing HeartbeatWorker: ${e.message}", e)
            Result.retry()
        }
    }

    private fun getBatteryInfo(): Pair<Int, Boolean> {
        val ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val batteryStatus: Intent? = context.registerReceiver(null, ifilter)

        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: 100
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: 100
        val batteryPct = if (level >= 0 && scale > 0) (level * 100 / scale) else 100

        val status = batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                status == BatteryManager.BATTERY_STATUS_FULL

        return Pair(batteryPct, isCharging)
    }

    private fun getNetworkType(): String {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
            ?: return "OFFLINE"

        val activeNetwork = cm.activeNetwork ?: return "OFFLINE"
        val caps = cm.getNetworkCapabilities(activeNetwork) ?: return "OFFLINE"

        return when {
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "CELLULAR"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "ETHERNET"
            else -> "CONNECTED"
        }
    }

    private fun checkPermissionsHealth(): PermissionState {
        val hasLoc = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        val hasBgLoc = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_BACKGROUND_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            hasLoc
        }

        val hasUsage = checkUsageStatsPermission()
        val hasAccessibility = checkAccessibilityPermission()
        val hasNotifListener = checkNotificationListenerPermission()
        val hasOverlay = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Settings.canDrawOverlays(context)
        } else {
            true
        }

        val powerManager = context.getSystemService(Context.POWER_SERVICE) as? PowerManager
        val hasBatteryOptIgnored = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && powerManager != null) {
            powerManager.isIgnoringBatteryOptimizations(context.packageName)
        } else {
            true
        }

        return PermissionState(
            hasLocationPermission = hasLoc,
            hasBackgroundLocation = hasBgLoc,
            hasUsageStats = hasUsage,
            hasAccessibility = hasAccessibility,
            hasNotificationListener = hasNotifListener,
            hasOverlayPermission = hasOverlay,
            hasBatteryOptimizationIgnored = hasBatteryOptIgnored,
            hasMediaProjection = MediaProjectionService.isRunning
        )
    }

    private fun checkUsageStatsPermission(): Boolean {
        val appOps = context.getSystemService(Context.APP_OPS_SERVICE) as? AppOpsManager ?: return false
        val mode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            appOps.unsafeCheckOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                context.packageName
            )
        } else {
            @Suppress("DEPRECATION")
            appOps.checkOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                context.packageName
            )
        }
        return mode == AppOpsManager.MODE_ALLOWED
    }

    private fun checkAccessibilityPermission(): Boolean {
        val expectedServiceName = "${context.packageName}/${ParentIQAccessibilityService::class.java.canonicalName}"
        val enabledServices = Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) ?: return false

        return enabledServices.contains(expectedServiceName) || enabledServices.contains(context.packageName)
    }

    private fun checkNotificationListenerPermission(): Boolean {
        val enabledPackages = NotificationManagerCompat.getEnabledListenerPackages(context)
        return enabledPackages.contains(context.packageName)
    }

    private fun syncAppUsageData() {
        try {
            val usageStatsManager = context.getSystemService(Context.USAGE_STATS_SERVICE) as? UsageStatsManager
                ?: return

            val calendar = Calendar.getInstance()
            val endTime = calendar.timeInMillis
            calendar.set(Calendar.HOUR_OF_DAY, 0)
            calendar.set(Calendar.MINUTE, 0)
            calendar.set(Calendar.SECOND, 0)
            val startTime = calendar.timeInMillis

            val usageStatsList = usageStatsManager.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY,
                startTime,
                endTime
            )

            if (!usageStatsList.isNullOrEmpty()) {
                val pm = context.packageManager
                val dateStr = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
                val appUsageItems = mutableListOf<AppUsageItem>()
                var totalScreenTimeSec = 0

                for (stat in usageStatsList) {
                    val foregroundSec = (stat.totalTimeInForeground / 1000).toInt()
                    if (foregroundSec > 10) { // filter out background glitches
                        totalScreenTimeSec += foregroundSec
                        val appName = try {
                            val appInfo = pm.getApplicationInfo(stat.packageName, 0)
                            pm.getApplicationLabel(appInfo).toString()
                        } catch (e: Exception) {
                            stat.packageName
                        }

                        appUsageItems.add(
                            AppUsageItem(
                                packageName = stat.packageName,
                                appName = appName,
                                category = categorizeApp(stat.packageName),
                                usageDate = dateStr,
                                foregroundTimeSeconds = foregroundSec,
                                launchCount = 1
                            )
                        )
                    }
                }

                if (appUsageItems.isNotEmpty()) {
                    apiClient.uploadAppUsage(AppUsageBatch(appUsageItems.take(20)))
                    apiClient.syncScreenTime(
                        ScreenTimeSyncRequest(
                            logDate = dateStr,
                            totalScreenTimeSeconds = totalScreenTimeSec,
                            unlockCount = 10
                        )
                    )
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error syncing app usage: ${e.message}")
        }
    }

    private fun syncInstalledApps() {
        try {
            val pm = context.packageManager
            val packages = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            val installedList = mutableListOf<InstalledAppItem>()

            for (app in packages) {
                val isSystem = (app.flags and ApplicationInfo.FLAG_SYSTEM) != 0
                if (!isSystem || app.packageName.contains("chrome") || app.packageName.contains("youtube")) {
                    val name = pm.getApplicationLabel(app).toString()
                    installedList.add(
                        InstalledAppItem(
                            packageName = app.packageName,
                            appName = name,
                            versionName = "1.0",
                            category = categorizeApp(app.packageName),
                            isSystemApp = isSystem
                        )
                    )
                }
            }

            if (installedList.isNotEmpty()) {
                apiClient.uploadAppInventory(InstalledAppBatch(installedList))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error syncing installed apps: ${e.message}")
        }
    }

    private fun categorizeApp(packageName: String): String {
        val lower = packageName.lowercase()
        return when {
            lower.contains("game") || lower.contains("roblox") || lower.contains("minecraft") -> "Games"
            lower.contains("youtube") || lower.contains("netflix") || lower.contains("video") || lower.contains("spotify") -> "Entertainment"
            lower.contains("instagram") || lower.contains("tiktok") || lower.contains("facebook") || lower.contains("snapchat") || lower.contains("twitter") -> "Social Media"
            lower.contains("chrome") || lower.contains("browser") || lower.contains("firefox") -> "Browsers"
            lower.contains("whatsapp") || lower.contains("telegram") || lower.contains("messenger") || lower.contains("discord") -> "Communication"
            lower.contains("duolingo") || lower.contains("khan") || lower.contains("learn") || lower.contains("classroom") -> "Education"
            else -> "Utilities"
        }
    }
}

