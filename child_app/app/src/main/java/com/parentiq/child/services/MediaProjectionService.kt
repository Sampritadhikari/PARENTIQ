package com.parentiq.child.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.DisplayMetrics
import android.util.Log
import android.view.WindowManager
import androidx.core.app.NotificationCompat
import com.parentiq.child.ParentIQChildApp
import com.parentiq.child.R
import com.parentiq.child.data.api.ApiClient
import com.parentiq.child.ui.MainActivity
import java.io.ByteArrayOutputStream
import java.util.concurrent.Executors

/**
 * Transparent, Disclosed MediaProjection Service.
 *
 * Implements Google Play and Android parental control guidelines:
 * 1. Prominently displays a persistent foreground notification whenever active.
 * 2. Informs child that parent is viewing the screen.
 * 3. Provides an immediate "Stop Sharing" button to revoke access.
 * 4. Never operates silently or in stealth mode.
 */
class MediaProjectionService : Service() {

    companion object {
        const val TAG = "MediaProjectionService"
        const val NOTIFICATION_ID = 2002
        const val ACTION_START = "com.parentiq.child.action.START_MEDIA_PROJECTION"
        const val ACTION_STOP = "com.parentiq.child.action.STOP_MEDIA_PROJECTION"
        const val EXTRA_RESULT_CODE = "extra_result_code"
        const val EXTRA_RESULT_DATA = "extra_result_data"
        const val EXTRA_SESSION_ID = "extra_session_id"

        var isRunning = false
            private set
    }

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var sessionId: String? = null
    private val backgroundExecutor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private lateinit var apiClient: ApiClient

    override fun onCreate() {
        super.onCreate()
        apiClient = ApiClient(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent == null) return START_NOT_STICKY

        when (intent.action) {
            ACTION_STOP -> {
                Log.i(TAG, "Stop action received by user or parent.")
                stopScreenShare()
                stopSelf()
                return START_NOT_STICKY
            }
            ACTION_START -> {
                sessionId = intent.getStringExtra(EXTRA_SESSION_ID)
                val resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0)
                val resultData = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra(EXTRA_RESULT_DATA, Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(EXTRA_RESULT_DATA)
                }

                if (resultCode != 0 && resultData != null) {
                    startForegroundWithTransparency()
                    setupMediaProjection(resultCode, resultData)
                    isRunning = true
                } else {
                    Log.e(TAG, "Invalid resultCode or data for MediaProjection")
                    stopSelf()
                }
            }
        }

        return START_NOT_STICKY
    }

    private fun startForegroundWithTransparency() {
        val stopIntent = Intent(this, MediaProjectionService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this,
            1,
            stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val openAppIntent = Intent(this, MainActivity::class.java)
        val openAppPendingIntent = PendingIntent.getActivity(
            this,
            0,
            openAppIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification: Notification = NotificationCompat.Builder(this, ParentIQChildApp.CHANNEL_MEDIA_PROJECTION)
            .setContentTitle("Screen Sharing Active")
            .setContentText("Your parent is viewing this screen with your permission.")
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setOngoing(true)
            .setContentIntent(openAppPendingIntent)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Stop Sharing", stopPendingIntent)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun setupMediaProjection(resultCode: Int, data: Intent) {
        val mpManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = mpManager.getMediaProjection(resultCode, data)

        mediaProjection?.registerCallback(object : MediaProjection.Callback() {
            override fun onStop() {
                super.onStop()
                Log.i(TAG, "MediaProjection stopped by system or permissions revoke.")
                stopScreenShare()
                stopSelf()
            }
        }, mainHandler)

        val windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val metrics = DisplayMetrics()
        @Suppress("DEPRECATION")
        windowManager.defaultDisplay.getRealMetrics(metrics)

        val width = 720
        val height = (720f * (metrics.heightPixels.toFloat() / metrics.widthPixels.toFloat())).toInt()
        val density = metrics.densityDpi

        imageReader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2)
        virtualDisplay = mediaProjection?.createVirtualDisplay(
            "ParentIQScreenShare",
            width,
            height,
            density,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader?.surface,
            null,
            null
        )

        imageReader?.setOnImageAvailableListener({ reader ->
            backgroundExecutor.execute {
                var image: android.media.Image? = null
                try {
                    image = reader.acquireLatestImage()
                    if (image != null) {
                        val planes = image.planes
                        val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride
                        val rowStride = planes[0].rowStride
                        val rowPadding = rowStride - pixelStride * width

                        val bitmap = Bitmap.createBitmap(
                            width + rowPadding / pixelStride,
                            height,
                            Bitmap.Config.ARGB_8888
                        )
                        bitmap.copyPixelsFromBuffer(buffer)

                        val croppedBitmap = Bitmap.createBitmap(bitmap, 0, 0, width, height)
                        val out = ByteArrayOutputStream()
                        croppedBitmap.compress(Bitmap.CompressFormat.JPEG, 60, out)
                        val jpegBytes = out.toByteArray()

                        // Ready for transmission to live session endpoint or WebRTC socket
                        Log.d(TAG, "Captured frame: ${jpegBytes.size} bytes for session $sessionId")

                        bitmap.recycle()
                        croppedBitmap.recycle()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error acquiring image frame: ${e.message}")
                } finally {
                    image?.close()
                }
            }
        }, mainHandler)
    }

    private fun stopScreenShare() {
        isRunning = false
        try {
            virtualDisplay?.release()
            virtualDisplay = null
            imageReader?.close()
            imageReader = null
            mediaProjection?.stop()
            mediaProjection = null
        } catch (e: Exception) {
            Log.e(TAG, "Error releasing MediaProjection resources: ${e.message}")
        }
        stopForeground(STOP_FOREGROUND_REMOVE)
    }

    override fun onDestroy() {
        super.onDestroy()
        stopScreenShare()
        backgroundExecutor.shutdown()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

