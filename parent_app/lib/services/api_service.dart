import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService extends ChangeNotifier {
  static const String defaultBaseUrl = 'http://127.0.0.1:8000/api/v1';
  String baseUrl;
  String? accessToken;
  String? refreshToken;
  String? currentUserId;
  String? currentUserName;

  ApiService({this.baseUrl = defaultBaseUrl});

  bool get isAuthenticated => accessToken != null;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (accessToken != null) 'Authorization': 'Bearer $accessToken',
      };

  // ----------------------------------------------------
  // Authentication
  // ----------------------------------------------------
  Future<bool> register(String email, String password, String name) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: _headers,
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': name,
      }),
    );
    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      accessToken = data['access_token'];
      refreshToken = data['refresh_token'];
      currentUserName = name;
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<bool> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: _headers,
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      accessToken = data['access_token'];
      refreshToken = data['refresh_token'];
      await fetchMe();
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<void> fetchMe() async {
    if (accessToken == null) return;
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      currentUserId = data['id'];
      currentUserName = data['full_name'];
      notifyListeners();
    }
  }

  void logout() {
    accessToken = null;
    refreshToken = null;
    currentUserId = null;
    currentUserName = null;
    notifyListeners();
  }

  // ----------------------------------------------------
  // Children & Dashboard
  // ----------------------------------------------------
  Future<List<ChildModel>> getChildren() async {
    final response = await http.get(
      Uri.parse('$baseUrl/children'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => ChildModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<ChildModel?> createChild(String name, int age, String gender) async {
    final response = await http.post(
      Uri.parse('$baseUrl/children'),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'age': age,
        'gender': gender,
      }),
    );
    if (response.statusCode == 201) {
      return ChildModel.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  Future<DashboardSummary?> getChildDashboard(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/children/$childId/dashboard'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return DashboardSummary.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  // ----------------------------------------------------
  // Location & Geofencing
  // ----------------------------------------------------
  Future<List<LocationLogModel>> getLocationHistory(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/location/history/$childId?limit=50'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => LocationLogModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<List<GeofenceModel>> getGeofences(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/location/geofences/$childId'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => GeofenceModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<GeofenceModel?> createGeofence(
      String childId, String name, double lat, double lon, double radius) async {
    final response = await http.post(
      Uri.parse('$baseUrl/location/geofences/$childId'),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'latitude': lat,
        'longitude': lon,
        'radius_meters': radius,
        'zone_type': 'safe',
        'notify_on_entry': true,
        'notify_on_exit': true,
      }),
    );
    if (response.statusCode == 201) {
      return GeofenceModel.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  Future<bool> deleteGeofence(String geofenceId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/location/geofences/$geofenceId'),
      headers: _headers,
    );
    return response.statusCode == 204;
  }

  // ----------------------------------------------------
  // Screen Time Controls
  // ----------------------------------------------------
  Future<ScreenTimeRuleModel?> getScreenTimeRules(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/screentime/rules/$childId'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return ScreenTimeRuleModel.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  Future<ScreenTimeRuleModel?> updateScreenTimeRules(
      String childId, Map<String, dynamic> updates) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/screentime/rules/$childId'),
      headers: _headers,
      body: jsonEncode(updates),
    );
    if (response.statusCode == 200) {
      return ScreenTimeRuleModel.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  Future<bool> grantBonusTime(String childId, int minutes, bool approved) async {
    final response = await http.post(
      Uri.parse('$baseUrl/screentime/bonus-action/$childId'),
      headers: _headers,
      body: jsonEncode({
        'minutes_granted': minutes,
        'approved': approved,
      }),
    );
    return response.statusCode == 200;
  }

  // ----------------------------------------------------
  // Application Management
  // ----------------------------------------------------
  Future<List<InstalledAppModel>> getInstalledApps(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/apps/installed/$childId'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => InstalledAppModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<List<AppUsageModel>> getAppUsages(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/apps/usage/$childId'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => AppUsageModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<AppRestrictionModel?> setAppRestriction(
    String childId,
    String packageName,
    String appName,
    bool isBlocked, {
    int? dailyLimitMinutes,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/apps/restrictions/$childId'),
      headers: _headers,
      body: jsonEncode({
        'package_name': packageName,
        'app_name': appName,
        'is_blocked': isBlocked,
        'daily_limit_minutes': dailyLimitMinutes,
        'block_during_school': true,
        'block_during_bedtime': true,
      }),
    );
    if (response.statusCode == 200) {
      return AppRestrictionModel.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  // ----------------------------------------------------
  // Online Safety & SOS
  // ----------------------------------------------------
  Future<List<SafetyAlertModel>> getSafetyAlerts(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/safety/alerts/$childId'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => SafetyAlertModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<bool> reviewSafetyAlert(String alertId) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/safety/alerts/$alertId/review'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ----------------------------------------------------
  // Live Monitoring (Approved Sessions)
  // ----------------------------------------------------
  Future<LiveSessionModel?> requestLiveSession(
      String deviceId, String sessionType) async {
    final response = await http.post(
      Uri.parse('$baseUrl/monitoring/request/$deviceId'),
      headers: _headers,
      body: jsonEncode({'session_type': sessionType}),
    );
    if (response.statusCode == 200) {
      return LiveSessionModel.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  Future<bool> terminateLiveSession(String sessionId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/monitoring/terminate/$sessionId'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ----------------------------------------------------
  // Reports & Analytics
  // ----------------------------------------------------
  Future<Map<String, dynamic>?> getReportsSummary(String childId,
      {int days = 7}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/reports/summary/$childId?days=$days'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  // ----------------------------------------------------
  // Device Pairing
  // ----------------------------------------------------
  Future<Map<String, dynamic>?> initiatePairing(String childId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/pairing/initiate/$childId'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  // ----------------------------------------------------
  // Notifications
  // ----------------------------------------------------
  Future<List<NotificationModel>> getNotifications() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => NotificationModel.fromJson(item)).toList();
    }
    return [];
  }

  Future<bool> markNotificationRead(String id) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/notifications/$id/read'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ----------------------------------------------------
  // Parent Settings & PIN
  // ----------------------------------------------------
  Future<Map<String, dynamic>> getPreferences() async {
    final response = await http.get(
      Uri.parse('$baseUrl/settings/preferences'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return {};
  }

  Future<bool> updatePreferences(Map<String, dynamic> prefs) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/settings/preferences'),
      headers: _headers,
      body: jsonEncode(prefs),
    );
    return response.statusCode == 200;
  }

  Future<bool> setPin(String pin) async {
    final response = await http.post(
      Uri.parse('$baseUrl/settings/set-pin'),
      headers: _headers,
      body: jsonEncode({'pin': pin}),
    );
    return response.statusCode == 200;
  }
}

