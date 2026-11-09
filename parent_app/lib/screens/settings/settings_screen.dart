import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';
import '../pairing/pairing_code_screen.dart';

class SettingsScreen extends StatefulWidget {
  final ChildModel child;
  final VoidCallback onLogout;

  const SettingsScreen({
    super.key,
    required this.child,
    required this.onLogout,
  });

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  Map<String, dynamic> _prefs = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final prefs = await api.getPreferences();
    if (mounted) {
      setState(() {
        _prefs = prefs;
        _isLoading = false;
      });
    }
  }

  Future<void> _updatePref(String key, bool val) async {
    setState(() => _prefs[key] = val);
    final api = context.read<ApiService>();
    await api.updatePreferences({key: val});
  }

  void _showSetPinDialog() {
    final pinCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Set Parent Security PIN'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'This PIN protects sensitive operations, rule adjustments, and unpairing actions.',
              style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: pinCtrl,
              keyboardType: TextInputType.number,
              obscureText: true,
              maxLength: 6,
              decoration: const InputDecoration(
                labelText: 'Enter 4-6 Digit PIN',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (pinCtrl.text.length >= 4) {
                Navigator.pop(ctx);
                final api = context.read<ApiService>();
                await api.setPin(pinCtrl.text);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Security PIN successfully configured.'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                }
              }
            },
            child: const Text('Save PIN'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final api = context.watch<ApiService>();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Parent Profile Card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  backgroundColor: AppColors.primaryNavy,
                  child: Text(
                    api.currentUserName?.isNotEmpty == true
                        ? api.currentUserName![0].toUpperCase()
                        : 'P',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        api.currentUserName ?? 'Parent Administrator',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Verified Parent Account',
                        style: TextStyle(fontSize: 12, color: AppColors.success),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),
        // Device Pairing Section
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Connected Child Devices',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                if (widget.child.devices.isEmpty)
                  const Text(
                    'No companion device currently connected to this profile.',
                    style: TextStyle(color: AppColors.textSecondary),
                  )
                else
                  ...widget.child.devices.map((dev) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const Icon(Icons.phone_android,
                            color: AppColors.primaryNavy),
                        title: Text(dev.deviceName),
                        subtitle: Text(
                            'Battery: ${dev.batteryLevel}% • ${dev.networkType.toUpperCase()}'),
                        trailing: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: dev.isOnline
                                ? AppColors.success.withOpacity(0.12)
                                : AppColors.textMuted.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            dev.isOnline ? 'CONNECTED' : 'STANDBY',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: dev.isOnline
                                  ? AppColors.success
                                  : AppColors.textSecondary,
                            ),
                          ),
                        ),
                      )),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (ctx) =>
                              PairingCodeScreen(child: widget.child),
                        ),
                      );
                    },
                    icon: const Icon(Icons.qr_code, size: 20),
                    label: const Text('Add or Re-Pair Device'),
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),
        // Security & Authentication
        Card(
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.pin, color: AppColors.secondaryRoyal),
                title: const Text('Parent Security PIN'),
                subtitle: const Text('Protect modifications & unpairing'),
                trailing: const Icon(Icons.chevron_right),
                onTap: _showSetPinDialog,
              ),
              const Divider(height: 1),
              const ListTile(
                leading: Icon(Icons.security, color: AppColors.secondaryRoyal),
                title: Text('Two-Factor Authentication'),
                subtitle: Text('Enabled via email verification'),
                trailing: Icon(Icons.check, color: AppColors.success),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),
        // Notification Preferences
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Notification Alerts',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Safe Zone Entry/Exit Alerts'),
                  value: _prefs['location_alerts'] ?? true,
                  activeColor: AppColors.primaryNavy,
                  onChanged: (v) => _updatePref('location_alerts', v),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Harmful Content & Cyberbullying'),
                  value: _prefs['safety_keyword_alerts'] ?? true,
                  activeColor: AppColors.primaryNavy,
                  onChanged: (v) => _updatePref('safety_keyword_alerts', v),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Daily Screen Time Limit Alerts'),
                  value: _prefs['screentime_alerts'] ?? true,
                  activeColor: AppColors.primaryNavy,
                  onChanged: (v) => _updatePref('screentime_alerts', v),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Newly Installed Applications'),
                  value: _prefs['app_install_alerts'] ?? true,
                  activeColor: AppColors.primaryNavy,
                  onChanged: (v) => _updatePref('app_install_alerts', v),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Low Battery Alerts (< 15%)'),
                  value: _prefs['battery_alerts'] ?? true,
                  activeColor: AppColors.primaryNavy,
                  onChanged: (v) => _updatePref('battery_alerts', v),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.danger,
              side: const BorderSide(color: AppColors.danger),
            ),
            onPressed: widget.onLogout,
            icon: const Icon(Icons.logout),
            label: const Text('Sign Out of PARENTIQ'),
          ),
        ),
      ],
    );
  }
}

