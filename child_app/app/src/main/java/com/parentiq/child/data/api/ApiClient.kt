package com.parentiq.child.data.api

import android.content.Context
import com.google.gson.Gson
import com.parentiq.child.data.models.*
import com.parentiq.child.data.storage.DevicePreferences
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class ApiClient(private val context: Context) {

    private val prefs = DevicePreferences(context)
    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()

    private fun buildRequest(endpoint: String, method: String, jsonBody: String? = null): Request {
        val url = "${prefs.serverUrl}$endpoint"
        val builder = Request.Builder().url(url)

        val token = prefs.deviceToken
        if (!token.isNullOrEmpty()) {
            builder.addHeader("Authorization", "Bearer $token")
        }

        when (method) {
            "POST" -> {
                val body = (jsonBody ?: "{}").toRequestBody(jsonMediaType)
                builder.post(body)
            }
            "PATCH" -> {
                val body = (jsonBody ?: "{}").toRequestBody(jsonMediaType)
                builder.patch(body)
            }
            else -> builder.get()
        }

        return builder.build()
    }

    fun verifyPairing(req: PairingRequest): PairingResponse? {
        val request = Request.Builder()
            .url("${prefs.serverUrl}/pairing/verify")
            .post(gson.toJson(req).toRequestBody(jsonMediaType))
            .build()

        return try {
            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val json = response.body?.string()
                gson.fromJson(json, PairingResponse::class.java)
            } else {
                null
            }
        } catch (e: IOException) {
            null
        }
    }

    fun sendHeartbeat(req: HeartbeatRequest): Boolean {
        val request = buildRequest("/devices/heartbeat", "POST", gson.toJson(req))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun uploadLocationBatch(batch: LocationBatch): Boolean {
        val request = buildRequest("/location/batch", "POST", gson.toJson(batch))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun uploadAppInventory(batch: InstalledAppBatch): Boolean {
        val request = buildRequest("/apps/inventory", "POST", gson.toJson(batch))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun uploadAppUsage(batch: AppUsageBatch): Boolean {
        val request = buildRequest("/apps/usage", "POST", gson.toJson(batch))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun syncScreenTime(sync: ScreenTimeSyncRequest): Boolean {
        val request = buildRequest("/screentime/sync", "POST", gson.toJson(sync))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun requestBonusTime(req: BonusTimeRequest): Boolean {
        val request = buildRequest("/screentime/bonus-request", "POST", gson.toJson(req))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun inspectContent(req: ContentInspectionRequest): Boolean {
        val request = buildRequest("/safety/inspect-content", "POST", gson.toJson(req))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun inspectUrl(req: URLInspectionRequest): Boolean {
        val request = buildRequest("/safety/inspect-url", "POST", gson.toJson(req))
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    fun triggerEmergencySos(): Boolean {
        val request = buildRequest("/safety/sos", "POST")
        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
}

