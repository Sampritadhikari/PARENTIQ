import 'package:test/test.dart';
import 'package:parent_app/models/models.dart';

void main() {
  test('ChildModel deserialization test', () {
    final json = {
      'id': 'child-123',
      'parent_id': 'parent-456',
      'name': 'Alex',
      'age': 12,
      'gender': 'female',
      'devices': [
        {
          'id': 'device-789',
          'device_name': 'Pixel 8',
          'is_online': true,
          'battery_level': 85,
          'is_charging': false,
          'network_type': 'wifi',
          'last_seen_at': DateTime.now().toIso8601String(),
        }
      ]
    };

    final child = ChildModel.fromJson(json);
    expect(child.id, 'child-123');
    expect(child.name, 'Alex');
    expect(child.age, 12);
    expect(child.devices.length, 1);
    expect(child.devices.first.batteryLevel, 85);
    expect(child.devices.first.isOnline, true);
  });

  test('DashboardSummary calculation deserialization test', () {
    final json = {
      'child_id': 'child-123',
      'child_name': 'Alex',
      'device_connected': true,
      'battery_level': 85,
      'is_charging': false,
      'network_type': 'wifi',
      'last_seen_at': DateTime.now().toIso8601String(),
      'today_screen_time_seconds': 5400,
      'daily_limit_minutes': 120,
      'top_apps': [
        {'app_name': 'YouTube', 'foreground_seconds': 3600}
      ],
      'unread_notifications_count': 2,
      'unreviewed_safety_alerts_count': 1,
      'instant_lock': false,
    };

    final summary = DashboardSummary.fromJson(json);
    expect(summary.todayScreenTimeSeconds, 5400);
    expect(summary.dailyLimitMinutes, 120);
    expect(summary.instantLock, false);
    expect(summary.topApps.length, 1);
  });
}
