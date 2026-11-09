import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class ScreenTimeScreen extends StatefulWidget {
  final ChildModel child;

  const ScreenTimeScreen({super.key, required this.child});

  @override
  State<ScreenTimeScreen> createState() => _ScreenTimeScreenState();
}

class _ScreenTimeScreenState extends State<ScreenTimeScreen> {
  ScreenTimeRuleModel? _rule;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadRules();
  }

  Future<void> _loadRules() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final rule = await api.getScreenTimeRules(widget.child.id);
    if (mounted) {
      setState(() {
        _rule = rule;
        _isLoading = false;
      });
    }
  }

  Future<void> _saveRules() async {
    if (_rule == null) return;
    final api = context.read<ApiService>();
    await api.updateScreenTimeRules(widget.child.id, {
      'daily_limit_minutes': _rule!.dailyLimitMinutes,
      'school_mode_enabled': _rule!.schoolModeEnabled,
      'school_mode_start': _rule!.schoolModeStart,
      'school_mode_end': _rule!.schoolModeEnd,
      'bedtime_mode_enabled': _rule!.bedtimeModeEnabled,
      'bedtime_start': _rule!.bedtimeStart,
      'bedtime_end': _rule!.bedtimeEnd,
      'instant_lock': _rule!.instantLock,
    });
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Screen time rules synchronized with child device.'),
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

    if (_rule == null) {
      return Center(
        child: ElevatedButton(
          onPressed: _loadRules,
          child: const Text('Load Rules'),
        ),
      );
    }

    final r = _rule!;

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _loadRules,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Instant Lock Card
            Card(
              color: r.instantLock
                  ? AppColors.danger.withOpacity(0.08)
                  : AppColors.surfaceWhite,
              child: SwitchListTile(
                title: const Text(
                  'Instant Device Lock',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                subtitle: Text(
                  r.instantLock
                      ? 'Child device is currently locked. Only emergency calls permitted.'
                      : 'Lock the child device immediately on demand.',
                  style: const TextStyle(fontSize: 13),
                ),
                value: r.instantLock,
                activeColor: AppColors.danger,
                onChanged: (val) {
                  setState(() => r.instantLock = val);
                  _saveRules();
                },
              ),
            ),

            const SizedBox(height: 16),
            // Daily Limit Slider Card
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
                          'Daily Screen Time Limit',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        Text(
                          '${r.dailyLimitMinutes ~/ 60}h ${r.dailyLimitMinutes % 60}m',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primaryNavy,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Applies automatically across all managed child applications.',
                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    ),
                    const SizedBox(height: 16),
                    Slider(
                      value: r.dailyLimitMinutes.toDouble(),
                      min: 15,
                      max: 480,
                      divisions: 31,
                      activeColor: AppColors.primaryNavy,
                      label: '${r.dailyLimitMinutes ~/ 60}h ${r.dailyLimitMinutes % 60}m',
                      onChanged: (val) {
                        setState(() => r.dailyLimitMinutes = val.round());
                      },
                      onChangeEnd: (val) => _saveRules(),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),
            // School Mode Card
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
                            Icon(Icons.school, color: AppColors.primaryNavy),
                            SizedBox(width: 8),
                            Text(
                              'School Mode',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        Switch(
                          value: r.schoolModeEnabled,
                          activeColor: AppColors.primaryNavy,
                          onChanged: (val) {
                            setState(() => r.schoolModeEnabled = val);
                            _saveRules();
                          },
                        ),
                      ],
                    ),
                    const Text(
                      'Blocks distracting entertainment and social apps during class hours.',
                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    ),
                    if (r.schoolModeEnabled) ...[
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _TimeBox(
                            label: 'Starts',
                            time: r.schoolModeStart,
                            onTap: () async {
                              final picked = await showTimePicker(
                                context: context,
                                initialTime: const TimeOfDay(hour: 8, minute: 30),
                              );
                              if (picked != null) {
                                setState(() {
                                  r.schoolModeStart =
                                      '${picked.hour.toString().padLeft(2, '0')}:${picked.minute.toString().padLeft(2, '0')}';
                                });
                                _saveRules();
                              }
                            },
                          ),
                          const Icon(Icons.arrow_forward, color: AppColors.textMuted),
                          _TimeBox(
                            label: 'Ends',
                            time: r.schoolModeEnd,
                            onTap: () async {
                              final picked = await showTimePicker(
                                context: context,
                                initialTime: const TimeOfDay(hour: 15, minute: 30),
                              );
                              if (picked != null) {
                                setState(() {
                                  r.schoolModeEnd =
                                      '${picked.hour.toString().padLeft(2, '0')}:${picked.minute.toString().padLeft(2, '0')}';
                                });
                                _saveRules();
                              }
                            },
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),
            // Bedtime Mode Card
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
                            Icon(Icons.bedtime, color: AppColors.secondaryRoyal),
                            SizedBox(width: 8),
                            Text(
                              'Bedtime Mode',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        Switch(
                          value: r.bedtimeModeEnabled,
                          activeColor: AppColors.secondaryRoyal,
                          onChanged: (val) {
                            setState(() => r.bedtimeModeEnabled = val);
                            _saveRules();
                          },
                        ),
                      ],
                    ),
                    const Text(
                      'Locks non-essential device usage overnight to ensure healthy sleep.',
                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    ),
                    if (r.bedtimeModeEnabled) ...[
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _TimeBox(
                            label: 'Bedtime',
                            time: r.bedtimeStart,
                            onTap: () async {
                              final picked = await showTimePicker(
                                context: context,
                                initialTime: const TimeOfDay(hour: 21, minute: 0),
                              );
                              if (picked != null) {
                                setState(() {
                                  r.bedtimeStart =
                                      '${picked.hour.toString().padLeft(2, '0')}:${picked.minute.toString().padLeft(2, '0')}';
                                });
                                _saveRules();
                              }
                            },
                          ),
                          const Icon(Icons.arrow_forward, color: AppColors.textMuted),
                          _TimeBox(
                            label: 'Wake up',
                            time: r.bedtimeEnd,
                            onTap: () async {
                              final picked = await showTimePicker(
                                context: context,
                                initialTime: const TimeOfDay(hour: 7, minute: 0),
                              );
                              if (picked != null) {
                                setState(() {
                                  r.bedtimeEnd =
                                      '${picked.hour.toString().padLeft(2, '0')}:${picked.minute.toString().padLeft(2, '0')}';
                                });
                                _saveRules();
                              }
                            },
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TimeBox extends StatelessWidget {
  final String label;
  final String time;
  final VoidCallback onTap;

  const _TimeBox({
    required this.label,
    required this.time,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          color: AppColors.backgroundLight,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.cardBorder),
        ),
        child: Column(
          children: [
            Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
            const SizedBox(height: 4),
            Text(
              time,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

