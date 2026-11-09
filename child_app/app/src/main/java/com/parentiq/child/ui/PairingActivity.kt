package com.parentiq.child.ui

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.parentiq.child.ParentIQChildApp
import com.parentiq.child.data.api.ApiClient
import com.parentiq.child.data.models.PairingRequest
import com.parentiq.child.data.storage.DevicePreferences
import com.parentiq.child.databinding.ActivityPairingBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.UUID

class PairingActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPairingBinding
    private lateinit var prefs: DevicePreferences
    private lateinit var apiClient: ApiClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPairingBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefs = DevicePreferences(this)
        apiClient = ApiClient(this)

        if (prefs.isPaired) {
            startActivity(Intent(this, MainActivity::class.java))
            finish()
            return
        }

        binding.etDeviceName.setText("${Build.MANUFACTURER} ${Build.MODEL}")
        binding.etServerUrl.setText(prefs.serverUrl)

        binding.btnVerifyPairing.setOnClickListener {
            attemptPairing()
        }
    }

    private fun attemptPairing() {
        val code = binding.etPairingCode.text?.toString()?.trim()?.uppercase() ?: ""
        val deviceName = binding.etDeviceName.text?.toString()?.trim() ?: "${Build.MANUFACTURER} ${Build.MODEL}"
        val serverUrl = binding.etServerUrl.text?.toString()?.trim() ?: ""

        if (code.length < 6) {
            binding.tvErrorMessage.text = "Please enter the valid 6-character code."
            binding.tvErrorMessage.visibility = View.VISIBLE
            return
        }

        if (serverUrl.isNotEmpty()) {
            prefs.serverUrl = serverUrl
        }

        binding.progressBar.visibility = View.VISIBLE
        binding.btnVerifyPairing.isEnabled = false
        binding.tvErrorMessage.visibility = View.GONE

        lifecycleScope.launch {
            val response = withContext(Dispatchers.IO) {
                val req = PairingRequest(
                    pairingCode = code,
                    deviceName = deviceName,
                    deviceModel = Build.MODEL,
                    osVersion = "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})",
                    appVersion = "1.0.0",
                    deviceFingerprint = "${Build.FINGERPRINT}_${UUID.randomUUID().toString().take(8)}"
                )
                apiClient.verifyPairing(req)
            }

            binding.progressBar.visibility = View.GONE
            binding.btnVerifyPairing.isEnabled = true

            if (response != null && response.deviceToken.isNotEmpty()) {
                prefs.deviceToken = response.deviceToken
                prefs.deviceId = response.deviceId
                prefs.childId = response.childId
                prefs.childName = response.childName

                Toast.makeText(this@PairingActivity, "Device paired successfully with ${response.childName}!", Toast.LENGTH_LONG).show()

                // Start Location Service
                ParentIQChildApp.startLocationServiceIfPermitted(this@PairingActivity)

                // Navigate to Permissions Health Setup
                val intent = Intent(this@PairingActivity, PermissionsActivity::class.java)
                startActivity(intent)
                finish()
            } else {
                binding.tvErrorMessage.text = "Invalid pairing code or server unreachable. Please verify code in Parent App."
                binding.tvErrorMessage.visibility = View.VISIBLE
            }
        }
    }
}

