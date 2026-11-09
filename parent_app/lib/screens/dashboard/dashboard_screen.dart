import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  final ChildModel child;
  final VoidCallback onNavigateToLocation;
  final VoidCallback onNavigateToLive;
  final VoidCallback onNavigateToScreenTime;

  const DashboardScreen({
    super.key,
    required this.child,
    required this.onNavigateToLocation,
    required this.onNavigateToLive,
    required this.onNavigateToScreenTime,
  });

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  DashboardSummary? _summary;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  @override
  void didUpdateWidget(covariant DashboardScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.child.id != widget.child.id) {
      _loadDashboard();
    }
  }

  Future<void> _loadDashboard() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final summary = await api.getChildDashboard(widget.child.id);
    if (mounted) {
      setState(() {
        _summary = summary;
        _isLoading = false;
      });
    }
  }

  Future<void> _toggleInstantLock() async {
    if (_summary == null) return;
    final api = context.read<ApiService>();
    final newLockState = !_summary!.instantLock;
    await api.updateScreenTimeRules(
      widget.child.id,
      {'instant_lock': newLockState},
    );
    _loadDashboard();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            newLockState
                ? 'Device has been locked instantly.'
                : 'Device has been unlocked.',
          ),
          backgroundColor: newLockState ? AppColors.danger : AppColors.success,
        ),
      );
    }
  }

  Future<void> _grantQuickBonus() async {
    final api = context.read<ApiService>();
    await api.grantBonusTime(widget.child.id, 15, true);
    _loadDashboard();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Granted +15 minutes screen time to child device.'),
          backgroundColor: AppColors.success,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_summary == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.phonelink_erase, size: 64, color: AppColors.textMuted),
            const SizedBox(height: 16),
            const Text(
              'No active device paired yet',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: _loadDashboard,
              child: const Text('Refresh'),
            ),
          ],
        ),
      );
    }

    final s = _summary!;
    final screenMinutesUsed = s.todayScreenTimeSeconds ~/ 60;
    final limitMinutes = s.dailyLimitMinutes > 0 ? s.dailyLimitMinutes : 120;
    final progress = (screenMinutesUsed / limitMinutes).clamp(0.0, 1.0);

    return RefreshIndicator(
      onRefresh: _loadDashboard,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Device Status Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      color: s.deviceConnected
                          ? AppColors.success.withOpacity(0.12)
                          : AppColors.danger.withOpacity(0.12),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      s.deviceConnected ? Icons.phone_android : Icons.phone_disabled,
                      color: s.deviceConnected ? AppColors.success : AppColors.danger,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              s.childName,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: s.deviceConnected
                                    ? AppColors.success.withOpacity(0.15)
                                    : AppColors.textMuted.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                s.deviceConnected ? 'ONLINE' : 'OFFLINE',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  color: s.deviceConnected
                                      ? AppColors.success
                                      : AppColors.textSecondary,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${s.networkType.toUpperCase()} • Last seen just now',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Row(
                        children: [
                          Icon(
                            s.isCharging
                                ? Icons.battery_charging_full
                                : Icons.battery_std,
                            color: s.batteryLevel < 20
                                ? AppColors.danger
                                : AppColors.primaryNavy,
                            size: 20,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${s.batteryLevel}%',
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      if (s.instantLock)
                        const Padding(
                          padding: EdgeInsets.only(top: 4),
                          child: Text(
                            'LOCKED',
                            style: TextStyle(
                              color: AppColors.danger,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Quick Action Bar
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _QuickActionButton(
                  icon: s.instantLock ? Icons.lock_open : Icons.lock_outline,
                  label: s.instantLock ? 'Unlock' : 'Instant Lock',
                  color: s.instantLock ? AppColors.success : AppColors.danger,
                  onTap: _toggleInstantLock,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _QuickActionButton(
                  icon: Icons.my_location,
                  label: 'Locate',
                  color: AppColors.info,
                  onTap: widget.onNavigateToLocation,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _QuickActionButton(
                  icon: Icons.add_alarm,
                  label: '+15 Min',
                  color: AppColors.warning,
                  onTap: _grantQuickBonus,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _QuickActionButton(
                  icon: Icons.videocam_outlined,
                  label: 'Live Stream',
                  color: AppColors.accentCyan,
                  onTap: widget.onNavigateToLive,
                ),
              ),
            ],
          ),

          // Safety Alert Banner (if unreviewed alerts exist)
          if (s.unreviewedSafetyAlertsCount > 0) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.danger.withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.danger.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded,
                      color: AppColors.danger, size: 28),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${s.unreviewedSafetyAlertsCount} Unreviewed Safety Alert(s)',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: AppColors.danger,
                          ),
                        ),
                        const Text(
                          'Sensitive keywords or inappropriate URLs detected.',
                          style: TextStyle(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],

          // Today's Screen Time Summary Card
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        "Today's Screen Time",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      TextButton(
                        onPressed: widget.onNavigateToScreenTime,
                        child: const Text('Manage Limits'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        '${screenMinutesUsed ~/ 60}h ${screenMinutesUsed % 60}m',
                        style: const TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: AppColors.primaryNavy,
                        ),
                      ),
                      Text(
                        ' / ${limitMinutes ~/ 60}h ${limitMinutes % 60}m limit',
                        style: const TextStyle(
                          fontSize: 14,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 10,
                      backgroundColor: AppColors.cardBorder,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        progress > 0.9 ? AppColors.danger : AppColors.accentCyan,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Current Location Preview Card
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.location_on, color: AppColors.danger, size: 20),
                          SizedBox(width: 6),
                          Text(
                            'Current Location',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                      TextButton(
                        onPressed: widget.onNavigateToLocation,
                        child: const Text('View Map'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    s.currentLocation != null
                        ? (s.currentLocation!['address'] ??
                            'Lat: ${s.currentLocation!['latitude']}, Lon: ${s.currentLocation!['longitude']}')
                        : 'Location tracking active • Acquiring GPS fix...',
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Top Most-Used Apps Today
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Most Used Apps Today',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (s.topApps.isEmpty)
                    const Text(
                      'No app activity logged yet today.',
                      style: TextStyle(color: AppColors.textMuted),
                    )
                  else
                    ...s.topApps.map((app) {
                      final name = app['app_name'] ?? 'Application';
                      final seconds = app['foreground_seconds'] ?? 0;
                      final minutes = seconds ~/ 60;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          children: [
                            Container(
                              width: 36,
                              height: 36,
                              decoration: BoxDecoration(
                                color: AppColors.secondaryRoyal.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(Icons.apps,
                                  color: AppColors.secondaryRoyal, size: 20),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                name,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            Text(
                              '${minutes}m',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

