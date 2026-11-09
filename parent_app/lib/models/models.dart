class ChildModel {
  final String id;
  final String parentId;
  final String name;
  final int? age;
  final String? gender;
  final String? avatarUrl;
  final List<DeviceSummaryModel> devices;

  ChildModel({
    required this.id,
    required this.parentId,
    required this.name,
    this.age,
    this.gender,
    this.avatarUrl,
    this.devices = const [],
  });

  factory ChildModel.fromJson(Map<String, dynamic> json) {
    return ChildModel(
      id: json['id'] ?? '',
      parentId: json['parent_id'] ?? '',
      name: json['name'] ?? '',
      age: json['age'],
      gender: json['gender'],
      avatarUrl: json['avatar_url'],
      devices: (json['devices'] as List<dynamic>?)
              ?.map((d) => DeviceSummaryModel.fromJson(d))
              .toList() ??
          [],
    );
  }
}

class DeviceSummaryModel {
  final String id;
  final String deviceName;
  final String? deviceModel;
  final String? osVersion;
  final bool isOnline;
  final int batteryLevel;
  final bool isCharging;
  final String networkType;
  final DateTime lastSeenAt;

  DeviceSummaryModel({
    required this.id,
    required this.deviceName,
    this.deviceModel,
    this.osVersion,
    required this.isOnline,
    required this.batteryLevel,
    required this.isCharging,
    required this.networkType,
    required this.lastSeenAt,
  });

  factory DeviceSummaryModel.fromJson(Map<String, dynamic> json) {
    return DeviceSummaryModel(
      id: json['id'] ?? '',
      deviceName: json['device_name'] ?? 'Android Device',
      deviceModel: json['device_model'],
      osVersion: json['os_version'],
      isOnline: json['is_online'] ?? false,
      batteryLevel: json['battery_level'] ?? 100,
      isCharging: json['is_charging'] ?? false,
      networkType: json['network_type'] ?? 'wifi',
      lastSeenAt: DateTime.tryParse(json['last_seen_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class DashboardSummary {
  final String childId;
  final String childName;
  final bool deviceConnected;
  final int batteryLevel;
  final bool isCharging;
  final String networkType;
  final DateTime lastSeenAt;
  final int todayScreenTimeSeconds;
  final int dailyLimitMinutes;
  final Map<String, dynamic>? currentLocation;
  final List<dynamic> topApps;
  final int unreadNotificationsCount;
  final int unreviewedSafetyAlertsCount;
  final bool instantLock;

  DashboardSummary({
    required this.childId,
    required this.childName,
    required this.deviceConnected,
    required this.batteryLevel,
    required this.isCharging,
    required this.networkType,
    required this.lastSeenAt,
    required this.todayScreenTimeSeconds,
    required this.dailyLimitMinutes,
    this.currentLocation,
    required this.topApps,
    required this.unreadNotificationsCount,
    required this.unreviewedSafetyAlertsCount,
    required this.instantLock,
  });

  factory DashboardSummary.fromJson(Map<String, dynamic> json) {
    return DashboardSummary(
      childId: json['child_id'] ?? '',
      childName: json['child_name'] ?? '',
      deviceConnected: json['device_connected'] ?? false,
      batteryLevel: json['battery_level'] ?? 0,
      isCharging: json['is_charging'] ?? false,
      networkType: json['network_type'] ?? 'none',
      lastSeenAt: DateTime.tryParse(json['last_seen_at'] ?? '') ?? DateTime.now(),
      todayScreenTimeSeconds: json['today_screen_time_seconds'] ?? 0,
      dailyLimitMinutes: json['daily_limit_minutes'] ?? 120,
      currentLocation: json['current_location'],
      topApps: json['top_apps'] ?? [],
      unreadNotificationsCount: json['unread_notifications_count'] ?? 0,
      unreviewedSafetyAlertsCount: json['unreviewed_safety_alerts_count'] ?? 0,
      instantLock: json['instant_lock'] ?? false,
    );
  }
}

class LocationLogModel {
  final String id;
  final double latitude;
  final double longitude;
  final double? accuracy;
  final double? speed;
  final String? address;
  final DateTime recordedAt;

  LocationLogModel({
    required this.id,
    required this.latitude,
    required this.longitude,
    this.accuracy,
    this.speed,
    this.address,
    required this.recordedAt,
  });

  factory LocationLogModel.fromJson(Map<String, dynamic> json) {
    return LocationLogModel(
      id: json['id'] ?? '',
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracy: (json['accuracy'] as num?)?.toDouble(),
      speed: (json['speed'] as num?)?.toDouble(),
      address: json['address'],
      recordedAt: DateTime.tryParse(json['recorded_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class GeofenceModel {
  final String id;
  final String name;
  final String zoneType;
  final double latitude;
  final double longitude;
  final double radiusMeters;
  final bool notifyOnEntry;
  final bool notifyOnExit;

  GeofenceModel({
    required this.id,
    required this.name,
    required this.zoneType,
    required this.latitude,
    required this.longitude,
    required this.radiusMeters,
    required this.notifyOnEntry,
    required this.notifyOnExit,
  });

  factory GeofenceModel.fromJson(Map<String, dynamic> json) {
    return GeofenceModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      zoneType: json['zone_type'] ?? 'safe',
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      radiusMeters: (json['radius_meters'] as num).toDouble(),
      notifyOnEntry: json['notify_on_entry'] ?? true,
      notifyOnExit: json['notify_on_exit'] ?? true,
    );
  }
}

class ScreenTimeRuleModel {
  final String id;
  final String childId;
  int dailyLimitMinutes;
  bool schoolModeEnabled;
  String schoolModeStart;
  String schoolModeEnd;
  List<int> schoolModeDays;
  bool bedtimeModeEnabled;
  String bedtimeStart;
  String bedtimeEnd;
  List<int> bedtimeDays;
  bool instantLock;

  ScreenTimeRuleModel({
    required this.id,
    required this.childId,
    required this.dailyLimitMinutes,
    required this.schoolModeEnabled,
    required this.schoolModeStart,
    required this.schoolModeEnd,
    required this.schoolModeDays,
    required this.bedtimeModeEnabled,
    required this.bedtimeStart,
    required this.bedtimeEnd,
    required this.bedtimeDays,
    required this.instantLock,
  });

  factory ScreenTimeRuleModel.fromJson(Map<String, dynamic> json) {
    return ScreenTimeRuleModel(
      id: json['id'] ?? '',
      childId: json['child_id'] ?? '',
      dailyLimitMinutes: json['daily_limit_minutes'] ?? 120,
      schoolModeEnabled: json['school_mode_enabled'] ?? false,
      schoolModeStart: json['school_mode_start'] ?? '08:30',
      schoolModeEnd: json['school_mode_end'] ?? '15:30',
      schoolModeDays: (json['school_mode_days'] as List<dynamic>?)
              ?.map((e) => e as int)
              .toList() ??
          [1, 2, 3, 4, 5],
      bedtimeModeEnabled: json['bedtime_mode_enabled'] ?? false,
      bedtimeStart: json['bedtime_start'] ?? '21:00',
      bedtimeEnd: json['bedtime_end'] ?? '07:00',
      bedtimeDays: (json['bedtime_days'] as List<dynamic>?)
              ?.map((e) => e as int)
              .toList() ??
          [0, 1, 2, 3, 4, 5, 6],
      instantLock: json['instant_lock'] ?? false,
    );
  }
}

class InstalledAppModel {
  final String id;
  final String packageName;
  final String appName;
  final String? versionName;
  final String category;
  final bool isSystemApp;

  InstalledAppModel({
    required this.id,
    required this.packageName,
    required this.appName,
    this.versionName,
    required this.category,
    required this.isSystemApp,
  });

  factory InstalledAppModel.fromJson(Map<String, dynamic> json) {
    return InstalledAppModel(
      id: json['id'] ?? '',
      packageName: json['package_name'] ?? '',
      appName: json['app_name'] ?? '',
      versionName: json['version_name'],
      category: json['category'] ?? 'Other',
      isSystemApp: json['is_system_app'] ?? false,
    );
  }
}

class AppUsageModel {
  final String packageName;
  final String appName;
  final String category;
  final int foregroundSeconds;
  final int launchCount;

  AppUsageModel({
    required this.packageName,
    required this.appName,
    required this.category,
    required this.foregroundSeconds,
    required this.launchCount,
  });

  factory AppUsageModel.fromJson(Map<String, dynamic> json) {
    return AppUsageModel(
      packageName: json['package_name'] ?? '',
      appName: json['app_name'] ?? '',
      category: json['category'] ?? 'Other',
      foregroundSeconds: json['foreground_time_seconds'] ?? 0,
      launchCount: json['launch_count'] ?? 0,
    );
  }
}

class AppRestrictionModel {
  final String packageName;
  final String appName;
  bool isBlocked;
  int? dailyLimitMinutes;
  bool blockDuringSchool;
  bool blockDuringBedtime;

  AppRestrictionModel({
    required this.packageName,
    required this.appName,
    required this.isBlocked,
    this.dailyLimitMinutes,
    required this.blockDuringSchool,
    required this.blockDuringBedtime,
  });

  factory AppRestrictionModel.fromJson(Map<String, dynamic> json) {
    return AppRestrictionModel(
      packageName: json['package_name'] ?? '',
      appName: json['app_name'] ?? '',
      isBlocked: json['is_blocked'] ?? false,
      dailyLimitMinutes: json['daily_limit_minutes'],
      blockDuringSchool: json['block_during_school'] ?? true,
      blockDuringBedtime: json['block_during_bedtime'] ?? true,
    );
  }
}

class SafetyAlertModel {
  final String id;
  final String alertType;
  final String severity;
  final String title;
  final String description;
  final String? sourceApp;
  final String? url;
  final bool isReviewed;
  final DateTime createdAt;

  SafetyAlertModel({
    required this.id,
    required this.alertType,
    required this.severity,
    required this.title,
    required this.description,
    this.sourceApp,
    this.url,
    required this.isReviewed,
    required this.createdAt,
  });

  factory SafetyAlertModel.fromJson(Map<String, dynamic> json) {
    return SafetyAlertModel(
      id: json['id'] ?? '',
      alertType: json['alert_type'] ?? 'warning',
      severity: json['severity'] ?? 'warning',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      sourceApp: json['source_app'],
      url: json['url'],
      isReviewed: json['is_reviewed'] ?? false,
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class NotificationModel {
  final String id;
  final String category;
  final String title;
  final String body;
  final bool isRead;
  final DateTime createdAt;

  NotificationModel({
    required this.id,
    required this.category,
    required this.title,
    required this.body,
    required this.isRead,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] ?? '',
      category: json['category'] ?? 'general',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      isRead: json['is_read'] ?? false,
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class LiveSessionModel {
  final String id;
  final String deviceId;
  final String sessionType;
  final String status;
  final bool explicitConsent;
  final String sessionToken;

  LiveSessionModel({
    required this.id,
    required this.deviceId,
    required this.sessionType,
    required this.status,
    required this.explicitConsent,
    required this.sessionToken,
  });

  factory LiveSessionModel.fromJson(Map<String, dynamic> json) {
    return LiveSessionModel(
      id: json['id'] ?? '',
      deviceId: json['device_id'] ?? '',
      sessionType: json['session_type'] ?? 'screen_mirror',
      status: json['status'] ?? 'requested',
      explicitConsent: json['explicit_child_consent'] ?? false,
      sessionToken: json['session_token'] ?? '',
    );
  }
}

