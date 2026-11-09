import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class SafetyScreen extends StatefulWidget {
  final ChildModel child;

  const SafetyScreen({super.key, required this.child});

  @override
  State<SafetyScreen> createState() => _SafetyScreenState();
}

class _SafetyScreenState extends State<SafetyScreen> {
  List<SafetyAlertModel> _alerts = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAlerts();
  }

  Future<void> _loadAlerts() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final alerts = await api.getSafetyAlerts(widget.child.id);
    if (mounted) {
      setState(() {
        _alerts = alerts;
        _isLoading = false;
      });
    }
  }

  Future<void> _markReviewed(String alertId) async {
    final api = context.read<ApiService>();
    await api.reviewSafetyAlert(alertId);
    _loadAlerts();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Safety alert marked as reviewed.'),
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

    final criticalAlerts = _alerts.where((a) => a.severity == 'critical').toList();
    final warnings = _alerts.where((a) => a.severity != 'critical').toList();

    return RefreshIndicator(
      onRefresh: _loadAlerts,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Safety Status Score Card
          Card(
            color: criticalAlerts.isNotEmpty
                ? AppColors.danger.withOpacity(0.08)
                : AppColors.success.withOpacity(0.08),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: criticalAlerts.isNotEmpty
                          ? AppColors.danger.withOpacity(0.2)
                          : AppColors.success.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      criticalAlerts.isNotEmpty
                          ? Icons.warning_rounded
                          : Icons.verified_user,
                      color: criticalAlerts.isNotEmpty
                          ? AppColors.danger
                          : AppColors.success,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          criticalAlerts.isNotEmpty
                              ? 'Action Required'
                              : 'Online Environment Secure',
                          style: TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.bold,
                            color: criticalAlerts.isNotEmpty
                                ? AppColors.danger
                                : AppColors.success,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_alerts.where((a) => !a.isReviewed).length} unreviewed security flags across apps & browsing.',
                          style: const TextStyle(
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
          ),

          // Emergency SOS Incidents (if any)
          if (criticalAlerts.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text(
              'Critical Safety Incidents',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.danger,
              ),
            ),
            const SizedBox(height: 8),
            ...criticalAlerts.map((alert) => _AlertCard(
                  alert: alert,
                  onReview: () => _markReviewed(alert.id),
                )),
          ],

          // Warning & Keyword Detection List
          const SizedBox(height: 16),
          const Text(
            'Safety & Keyword Detections',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          if (warnings.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(
                  child: Column(
                    children: [
                      Icon(Icons.check_circle_outline,
                          color: AppColors.success, size: 48),
                      SizedBox(height: 8),
                      Text(
                        'No cyberbullying, suspicious URLs, or harmful content detected.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
              ),
            )
          else
            ...warnings.map((alert) => _AlertCard(
                  alert: alert,
                  onReview: () => _markReviewed(alert.id),
                )),
        ],
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final SafetyAlertModel alert;
  final VoidCallback onReview;

  const _AlertCard({required this.alert, required this.onReview});

  @override
  Widget build(BuildContext context) {
    final isCritical = alert.severity == 'critical';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isCritical
              ? AppColors.danger.withOpacity(0.5)
              : AppColors.cardBorder,
          width: isCritical ? 1.5 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isCritical ? Icons.emergency : Icons.warning_amber_rounded,
                  color: isCritical ? AppColors.danger : AppColors.warning,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    alert.title,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                ),
                if (alert.isReviewed)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.success.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      'REVIEWED',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: AppColors.success,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(alert.description, style: const TextStyle(fontSize: 13)),
            if (alert.sourceApp != null) ...[
              const SizedBox(height: 6),
              Text(
                'Source Application: ${alert.sourceApp}',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  DateFormat.yMMMd().add_jm().format(alert.createdAt.toLocal()),
                  style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                ),
                if (!alert.isReviewed)
                  TextButton.icon(
                    onPressed: onReview,
                    icon: const Icon(Icons.check, size: 16),
                    label: const Text('Acknowledge'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

