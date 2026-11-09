package com.parentiq.child.services

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import com.parentiq.child.data.api.ApiClient
import com.parentiq.child.data.models.ContentInspectionRequest
import java.util.concurrent.Executors

class NotificationSafetyListenerService : NotificationListenerService() {

    private lateinit var apiClient: ApiClient
    private val executor = Executors.newSingleThreadExecutor()

    override fun onCreate() {
        super.onCreate()
        apiClient = ApiClient(this)
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        if (sbn == null) return

        val pkg = sbn.packageName ?: ""
        // Skip self notifications and system download/charging indicators
        if (pkg == packageName || pkg.contains("android") || pkg.contains("systemui")) {
            return
        }

        val extras = sbn.notification.extras ?: return
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""

        val combinedContent = "$title $text".trim()
        if (combinedContent.isNotEmpty() && combinedContent.length > 3) {
            executor.execute {
                apiClient.inspectContent(
                    ContentInspectionRequest(
                        content = combinedContent,
                        sourceApp = pkg
                    )
                )
            }
        }
    }
}

