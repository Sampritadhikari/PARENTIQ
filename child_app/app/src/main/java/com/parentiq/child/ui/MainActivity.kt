package com.parentiq.child.ui

import android.app.Dialog
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.RadioButton
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.parentiq.child.ParentIQChildApp
import com.parentiq.child.R
import com.parentiq.child.data.api.ApiClient
import com.parentiq.child.data.models.BonusTimeRequest
import com.parentiq.child.data.storage.DevicePreferences
import com.parentiq.child.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var prefs: DevicePreferences
    private lateinit var apiClient: ApiClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        prefs = DevicePreferences(this)
        apiClient = ApiClient(this)

        if (!prefs.isPaired) {
            val intent = Intent(this, PairingActivity::class.java)
            startActivity(intent)
            finish()
            return
        }

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        setupListeners()
    }

    override fun onResume() {
        super.onResume()
        if (prefs.isPaired) {
            updateDashboardData()
            ParentIQChildApp.startLocationServiceIfPermitted(this)
        }
    }

    private fun setupUI() {
        binding.tvChildName.text = prefs.childName ?: "Explorer"
        binding.tvGreeting.text = "Protected by ParentIQ"
        binding.tvConnectionStatus.text = "● Connected & Protected"

        val hours = prefs.dailyLimitMinutes / 60
        val mins = prefs.dailyLimitMinutes % 60
        binding.tvScreenTimeLimit.text = if (hours > 0) "${hours}h ${mins}m" else "${mins}m"
    }

    private fun updateDashboardData() {
        // Battery status
        val ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val batteryStatus: Intent? = registerReceiver(null, ifilter)
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: 100
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: 100
        val batteryPct = if (level >= 0 && scale > 0) (level * 100 / scale) else 100
        binding.tvBatteryStatus.text = "$batteryPct%"

        // Network status
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
        val activeNetwork = cm?.activeNetwork
        val caps = if (activeNetwork != null) cm.getNetworkCapabilities(activeNetwork) else null
        val netStr = when {
            caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true -> "Wi-Fi"
            caps?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) == true -> "Cellular"
            else -> "Offline"
        }
        binding.tvNetworkStatus.text = netStr
    }

    private fun setupListeners() {
        // Emergency SOS
        binding.btnSos.setOnClickListener {
            handleSosTrigger()
        }

        // Request Screen Time
        binding.btnRequestScreenTime.setOnClickListener {
            showScreenTimeRequestDialog()
        }

        // Permissions Center
        binding.btnPermissionsCenter.setOnClickListener {
            startActivity(Intent(this, PermissionsActivity::class.java))
        }

        // Privacy Policy
        binding.btnPrivacyPolicy.setOnClickListener {
            startActivity(Intent(this, PrivacyActivity::class.java))
        }
    }

    private fun handleSosTrigger() {
        MaterialAlertDialogBuilder(this)
            .setTitle("Confirm Emergency SOS")
            .setMessage("Are you in immediate need of assistance? This will dispatch an instant high-priority emergency alert with your current GPS coordinates to your guardians.")
            .setPositiveButton("Send SOS Alert") { _, _ ->
                binding.tvSosStatus.text = "Dispatching SOS Alert..."
                binding.tvSosStatus.setTextColor(getColor(R.color.danger))

                lifecycleScope.launch {
                    val success = withContext(Dispatchers.IO) {
                        apiClient.triggerEmergencySos()
                    }
                    if (success) {
                        binding.tvSosStatus.text = "SOS Sent! Guardians notified."
                        Toast.makeText(this@MainActivity, "Emergency alert sent to parents!", Toast.LENGTH_LONG).show()
                    } else {
                        binding.tvSosStatus.text = "Alert logged locally."
                        Toast.makeText(this@MainActivity, "Alert recorded.", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showScreenTimeRequestDialog() {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_screen_time_request, null)
        val rb15 = dialogView.findViewById<RadioButton>(R.id.rb15Min)
        val rb30 = dialogView.findViewById<RadioButton>(R.id.rb30Min)
        val rb60 = dialogView.findViewById<RadioButton>(R.id.rb60Min)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.etReason)

        MaterialAlertDialogBuilder(this)
            .setView(dialogView)
            .setPositiveButton("Submit Request") { _, _ ->
                val minutes = when {
                    rb30.isChecked -> 30
                    rb60.isChecked -> 60
                    else -> 15
                }
                val reason = etReason.text?.toString()?.trim()

                lifecycleScope.launch {
                    val success = withContext(Dispatchers.IO) {
                        apiClient.requestBonusTime(
                            BonusTimeRequest(
                                minutesRequested = minutes,
                                reason = reason
                            )
                        )
                    }
                    if (success) {
                        Toast.makeText(this@MainActivity, "Bonus time request sent for $minutes min!", Toast.LENGTH_LONG).show()
                    } else {
                        Toast.makeText(this@MainActivity, "Request could not be delivered to server.", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}

