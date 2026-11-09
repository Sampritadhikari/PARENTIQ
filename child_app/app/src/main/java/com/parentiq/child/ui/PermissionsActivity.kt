package com.parentiq.child.ui

import android.Manifest
import android.annotation.SuppressLint
import android.app.AppOpsManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.os.Process
import android.provider.Settings
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.parentiq.child.ParentIQChildApp
import com.parentiq.child.R
import com.parentiq.child.databinding.ActivityPermissionsBinding
import com.parentiq.child.services.ParentIQAccessibilityService

class PermissionsActivity : AppCompatActivity() {

    companion object {
        private const val REQ_LOCATION = 101
    }

    private lateinit var binding: ActivityPermissionsBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPermissionsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupButtons()
    }

    override fun onResume() {
        super.onResume()
        refreshPermissionStates()
    }

    private fun setupButtons() {
        binding.btnGrantLocation.setOnClickListener {
            val permissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION,
                    Manifest.permission.ACCESS_BACKGROUND_LOCATION
                )
            } else {
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            }
            ActivityCompat.requestPermissions(this, permissions, REQ_LOCATION)
        }

        binding.btnGrantUsage.setOnClickListener {
            val intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
            startActivity(intent)
        }

        binding.btnGrantAccessibility.setOnClickListener {
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            startActivity(intent)
        }

        binding.btnGrantNotification.setOnClickListener {
            val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
            startActivity(intent)
        }

        binding.btnGrantBattery.setOnClickListener {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                @SuppressLint("BatteryLife")
                val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
                    data = Uri.parse("package:$packageName")
                }
                startActivity(intent)
            }
        }

        binding.btnDone.setOnClickListener {
            ParentIQChildApp.startLocationServiceIfPermitted(this)
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
            finish()
        }
    }

    private fun refreshPermissionStates() {
        // 1. Location
        val hasFineLoc = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        updateBadge(binding.tvStatusLocation, hasFineLoc)

        // 2. Usage Stats
        val hasUsage = checkUsageStatsPermission()
        updateBadge(binding.tvStatusUsage, hasUsage)

        // 3. Accessibility
        val hasAccessibility = checkAccessibilityPermission()
        updateBadge(binding.tvStatusAccessibility, hasAccessibility)

        // 4. Notification Listener
        val hasNotification = NotificationManagerCompat.getEnabledListenerPackages(this).contains(packageName)
        updateBadge(binding.tvStatusNotification, hasNotification)

        // 5. Battery Optimization
        val powerManager = getSystemService(Context.POWER_SERVICE) as? PowerManager
        val hasBattery = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && powerManager != null) {
            powerManager.isIgnoringBatteryOptimizations(packageName)
        } else {
            true
        }
        updateBadge(binding.tvStatusBattery, hasBattery)
    }

    private fun updateBadge(textView: android.widget.TextView, isGranted: Boolean) {
        if (isGranted) {
            textView.text = "Granted"
            textView.setBackgroundResource(R.drawable.bg_badge_active)
            textView.setTextColor(ContextCompat.getColor(this, R.color.success))
        } else {
            textView.text = "Not Granted"
            textView.setBackgroundResource(R.drawable.bg_badge_inactive)
            textView.setTextColor(ContextCompat.getColor(this, R.color.danger))
        }
    }

    private fun checkUsageStatsPermission(): Boolean {
        val appOps = getSystemService(Context.APP_OPS_SERVICE) as? AppOpsManager ?: return false
        val mode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            appOps.unsafeCheckOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                packageName
            )
        } else {
            @Suppress("DEPRECATION")
            appOps.checkOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                packageName
            )
        }
        return mode == AppOpsManager.MODE_ALLOWED
    }

    private fun checkAccessibilityPermission(): Boolean {
        val expectedServiceName = "$packageName/${ParentIQAccessibilityService::class.java.canonicalName}"
        val enabledServices = Settings.Secure.getString(
            contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) ?: return false
        return enabledServices.contains(expectedServiceName) || enabledServices.contains(packageName)
    }
}

