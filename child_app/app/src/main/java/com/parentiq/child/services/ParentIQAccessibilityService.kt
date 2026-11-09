package com.parentiq.child.services

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Toast
import com.parentiq.child.data.api.ApiClient
import com.parentiq.child.data.models.URLInspectionRequest
import com.parentiq.child.data.storage.DevicePreferences
import java.util.concurrent.Executors

class ParentIQAccessibilityService : AccessibilityService() {

    private lateinit var apiClient: ApiClient
    private lateinit var prefs: DevicePreferences
    private val executor = Executors.newSingleThreadExecutor()
    private var lastInspectedUrl = ""

    override fun onServiceConnected() {
        super.onServiceConnected()
        apiClient = ApiClient(this)
        prefs = DevicePreferences(this)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        // 1. Check if device is in Instant Lock Mode
        if (prefs.isInstantLocked) {
            val packageName = event.packageName?.toString() ?: ""
            if (!isEssentialSystemApp(packageName)) {
                performGlobalAction(GLOBAL_ACTION_HOME)
                Toast.makeText(
                    this,
                    "Device is locked by parental schedule or instant lock.",
                    Toast.LENGTH_SHORT
                ).show()
                return
            }
        }

        // 2. Check Browser URLs
        val rootNode = rootInActiveWindow ?: return
        val url = findBrowserUrl(rootNode)
        if (!url.isNullOrEmpty() && url != lastInspectedUrl) {
            lastInspectedUrl = url
            executor.execute {
                val blocked = apiClient.inspectUrl(
                    URLInspectionRequest(url = url, sourceApp = event.packageName?.toString() ?: "Browser")
                )
                if (blocked) {
                    performGlobalAction(GLOBAL_ACTION_BACK)
                }
            }
        }
    }

    private fun findBrowserUrl(node: AccessibilityNodeInfo): String? {
        val viewId = node.viewIdResourceName
        if (viewId != null && (viewId.contains("url_bar") || viewId.contains("location_bar") || viewId.contains("search_box"))) {
            return node.text?.toString()
        }
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val found = findBrowserUrl(child)
            if (found != null) return found
        }
        return null
    }

    private fun isEssentialSystemApp(pkg: String): Boolean {
        return pkg.contains("dialer") || pkg.contains("phone") || pkg.contains("emergency") || pkg == packageName
    }

    override fun onInterrupt() {}
}

