import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class MonitoringScreen extends StatefulWidget {
  final ChildModel child;

  const MonitoringScreen({super.key, required this.child});

  @override
  State<MonitoringScreen> createState() => _MonitoringScreenState();
}

class _MonitoringScreenState extends State<MonitoringScreen> {
  LiveSessionModel? _activeSession;
  bool _isRequesting = false;

  Future<void> _startSession(String type) async {
    final device = widget.child.devices.isNotEmpty ? widget.child.devices.first : null;
    if (device == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No active child device found to connect to.')),
      );
      return;
    }

    setState(() => _isRequesting = true);
    final api = context.read<ApiService>();
    final session = await api.requestLiveSession(device.id, type);
    if (mounted) {
      setState(() {
        _activeSession = session;
        _isRequesting = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Session request dispatched. Waiting for child device authorization...',
          ),
          backgroundColor: AppColors.info,
        ),
      );
    }
  }

  Future<void> _stopSession() async {
    if (_activeSession == null) return;
    final api = context.read<ApiService>();
    await api.terminateLiveSession(_activeSession!.id);
    if (mounted) {
      setState(() {
        _activeSession = null;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Live monitoring session terminated.'),
          backgroundColor: AppColors.primaryNavy,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Privacy & Transparency Commitment Banner
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.accentCyan.withOpacity(0.08),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.accentCyan.withOpacity(0.3)),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.privacy_tip_outlined, color: AppColors.accentCyan, size: 28),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Disclosed & Approved Live Sessions',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                        color: AppColors.primaryNavy,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'In full compliance with child safety and transparency standards, sessions require explicit on-screen authorization on the child device. A persistent indicator is shown at all times during active sharing.',
                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // Stream Preview Container
        Card(
          clipBehavior: Clip.antiAlias,
          child: Column(
            children: [
              Container(
                height: 260,
                width: double.infinity,
                color: Colors.black,
                child: Stack(
                  children: [
                    if (_activeSession != null)
                      Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.screen_share,
                                color: AppColors.accentCyan, size: 64),
                            const SizedBox(height: 12),
                            Text(
                              'Active Session: ${_activeSession!.sessionType.toUpperCase()}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: AppColors.success,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                '• REC / LIVE STREAMING',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      )
                    else
                      const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.videocam_off_outlined,
                                color: Colors.white38, size: 54),
                            SizedBox(height: 12),
                            Text(
                              'No Active Live Stream',
                              style: TextStyle(
                                color: Colors.white70,
                                fontWeight: FontWeight.w600,
                                fontSize: 16,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Select an approved session below to begin.',
                              style: TextStyle(color: Colors.white38, fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              if (_activeSession != null)
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Session Token: ${_activeSession!.sessionToken.substring(0, 10)}...',
                        style: const TextStyle(
                            fontSize: 12, color: AppColors.textSecondary),
                      ),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.danger,
                        ),
                        onPressed: _stopSession,
                        icon: const Icon(Icons.stop, size: 18),
                        label: const Text('End Stream'),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),

        const SizedBox(height: 20),
        const Text(
          'Approved Session Controls',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 12),

        // Session Actions
        Row(
          children: [
            Expanded(
              child: _SessionOptionCard(
                icon: Icons.cast_connected,
                title: 'Screen Mirror',
                description: 'View child device screen in real-time.',
                isLoading: _isRequesting,
                onTap: () => _startSession('screen_mirror'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _SessionOptionCard(
                icon: Icons.camera_alt_outlined,
                title: 'Camera Snapshot',
                description: 'Approved snapshot with user notice.',
                isLoading: _isRequesting,
                onTap: () => _startSession('snapshot'),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _SessionOptionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final bool isLoading;
  final VoidCallback onTap;

  const _SessionOptionCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.isLoading,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: isLoading ? null : onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, color: AppColors.primaryNavy, size: 32),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

