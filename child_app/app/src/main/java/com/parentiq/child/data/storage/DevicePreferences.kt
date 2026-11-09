package com.parentiq.child.data.storage

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class DevicePreferences(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "parentiq_secure_device_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    var deviceToken: String?
        get() = prefs.getString("device_token", null)
        set(value) = prefs.edit().putString("device_token", value).apply()

    var deviceId: String?
        get() = prefs.getString("device_id", null)
        set(value) = prefs.edit().putString("device_id", value).apply()

    var childId: String?
        get() = prefs.getString("child_id", null)
        set(value) = prefs.edit().putString("child_id", value).apply()

    var childName: String?
        get() = prefs.getString("child_name", "Child")
        set(value) = prefs.edit().putString("child_name", value).apply()

    var serverUrl: String
        get() = prefs.getString("server_url", "http://10.0.2.2:8000/api/v1") ?: "http://10.0.2.2:8000/api/v1"
        set(value) = prefs.edit().putString("server_url", value).apply()

    val isPaired: Boolean
        get() = !deviceToken.isNullOrEmpty()

    var isInstantLocked: Boolean
        get() = prefs.getBoolean("is_instant_locked", false)
        set(value) = prefs.edit().putBoolean("is_instant_locked", value).apply()

    var dailyLimitMinutes: Int
        get() = prefs.getInt("daily_limit_minutes", 120)
        set(value) = prefs.edit().putInt("daily_limit_minutes", value).apply()

    fun clearAll() {
        prefs.edit().clear().apply()
    }
}

