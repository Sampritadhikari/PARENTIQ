import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class ReportsScreen extends StatefulWidget {
  final ChildModel child;

  const ReportsScreen({super.key, required this.child});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  Map<String, dynamic>? _report;
  int _selectedDays = 7;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadReport();
  }

  Future<void> _loadReport() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final rep = await api.getReportsSummary(widget.child.id, days: _selectedDays);
    if (mounted) {
      setState(() {
        _report = rep;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final trend = (_report?['screen_time_trend'] as List<dynamic>?) ?? [];
    final categories = (_report?['categories_breakdown'] as List<dynamic>?) ?? [];
    final safetyAlerts = _report?['total_safety_alerts'] ?? 0;
    final placesCount = _report?['locations_recorded'] ?? 0;

    return RefreshIndicator(
      onRefresh: _loadReport,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Range Filter
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [7, 14, 30].map((days) {
              final isSelected = _selectedDays == days;
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6),
                child: ChoiceChip(
                  label: Text('Last $days Days'),
                  selected: isSelected,
                  selectedColor: AppColors.primaryNavy.withOpacity(0.15),
                  onSelected: (val) {
                    setState(() => _selectedDays = days);
                    _loadReport();
                  },
                ),
              );
            }).toList(),
          ),

          const SizedBox(height: 16),

          // High-level Stats Overview
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  title: 'Places Visited',
                  value: '$placesCount',
                  icon: Icons.place_outlined,
                  color: AppColors.info,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  title: 'Safety Flags',
                  value: '$safetyAlerts',
                  icon: Icons.shield_outlined,
                  color: safetyAlerts > 0 ? AppColors.warning : AppColors.success,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Daily Screen Time Trend Chart Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Daily Screen Time Activity (Minutes)',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  if (trend.isEmpty)
                    const Text('No data recorded for this period.')
                  else
                    SizedBox(
                      height: 160,
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: trend.map((day) {
                          final minutes = day['minutes'] as int;
                          final label = day['day_of_week'] ?? '';
                          final heightFactor = (minutes / 240.0).clamp(0.05, 1.0);

                          return Expanded(
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 4),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  Text(
                                    '${minutes}m',
                                    style: const TextStyle(
                                      fontSize: 9,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Container(
                                    height: 110 * heightFactor,
                                    decoration: BoxDecoration(
                                      color: minutes > 180
                                          ? AppColors.danger
                                          : AppColors.accentCyan,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    label,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // App Category Breakdown Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'App Category Breakdown',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  if (categories.isEmpty)
                    const Text(
                      'No category data available.',
                      style: TextStyle(color: AppColors.textMuted),
                    )
                  else
                    ...categories.map((c) {
                      final name = c['category'] ?? 'Other';
                      final minutes = c['minutes'] ?? 0;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          children: [
                            Container(
                              width: 12,
                              height: 12,
                              decoration: const BoxDecoration(
                                color: AppColors.secondaryRoyal,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                name,
                                style: const TextStyle(fontWeight: FontWeight.w600),
                              ),
                            ),
                            Text(
                              '${minutes ~/ 60}h ${minutes % 60}m',
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

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 12),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }
}

