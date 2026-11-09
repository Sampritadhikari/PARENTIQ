package com.parentiq.child

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.content.ContextCompat
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.parentiq.child.data.storage.DevicePreferences
import com.parentiq.child.services.HeartbeatWorker
import com.parentiq.child.services.LocationTrackingService
import java.util.concurrent.TimeUnit

class ParentIQChildApp : Application() {

    companion object {
        const val TAG = "ParentIQChildApp"
        const val CHANNEL_LOCATION_TRACKING = "parentiq_location_channel"
        const val CHANNEL_MEDIA_PROJECTION = "parentiq_projection_channel"
        const val CHANNEL_SAFETY_ALERTS = "parentiq_safety_channel"

        fun startLocationServiceIfPermitted(context: Context) {
            val prefs = DevicePreferences(context)
            if (prefs.isPaired) {
                try {
                    val intent = Intent(context, LocationTrackingService::class.java).apply {
                        action = LocationTrackingService.ACTION_START
                    }
                    ContextCompat.startForegroundService(context, intent)
                    Log.i(TAG, "LocationTrackingService started successfully.")
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to start LocationTrackingService: ${e.message}")
                }
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
        scheduleHeartbeatWorker()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            // 1. Location Tracking Channel (Low importance, ongoing, non-intrusive)
            val locationChannel = NotificationChannel(
                CHANNEL_LOCATION_TRACKING,
                getString(R.string.location_service_channel),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notifies child that background location sharing is active."
                setShowBadge(false)
            }

            // 2. Media Projection / Live Sharing Channel (High importance, visible indicator)
            val projectionChannel = NotificationChannel(
                CHANNEL_MEDIA_PROJECTION,
                getString(R.string.media_projection_channel),
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Transparent indicator shown when parent is viewing screen with permission."
                enableVibration(true)
                setShowBadge(true)
            }

            // 3. Safety Alerts Channel
            val safetyChannel = NotificationChannel(
                CHANNEL_SAFETY_ALERTS,
                getString(R.string.general_channel),
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Alerts regarding parental control, screen time limits, and safety status."
            }

            notificationManager.createNotificationChannels(
                listOf(locationChannel, projectionChannel, safetyChannel)
            )
        }
    }

    private fun scheduleHeartbeatWorker() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val heartbeatWorkRequest = PeriodicWorkRequestBuilder<HeartbeatWorker>(
            15, TimeUnit.MINUTES,
            5, TimeUnit.MINUTES
        )
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "ParentIQHeartbeatWorker",
            ExistingPeriodicWorkPolicy.KEEP,
            heartbeatWorkRequest
        )
        Log.i(TAG, "Enqueued periodic HeartbeatWorker (15m interval).")
    }
}

