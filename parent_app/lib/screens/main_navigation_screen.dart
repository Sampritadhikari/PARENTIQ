import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme/app_theme.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import 'dashboard/dashboard_screen.dart';
import 'location/location_screen.dart';
import 'screentime/screentime_screen.dart';
import 'apps/apps_screen.dart';
import 'safety/safety_screen.dart';
import 'monitoring/monitoring_screen.dart';
import 'reports/reports_screen.dart';
import 'settings/settings_screen.dart';

class MainNavigationScreen extends StatefulWidget {
  final VoidCallback onLogout;

  const MainNavigationScreen({super.key, required this.onLogout});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;
  List<ChildModel> _children = [];
  ChildModel? _selectedChild;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadChildren();
  }

  Future<void> _loadChildren() async {
    final api = context.read<ApiService>();
    final children = await api.getChildren();
    if (mounted) {
      setState(() {
        _children = children;
        if (children.isNotEmpty) {
          _selectedChild = children.first;
        }
        _isLoading = false;
      });
    }
  }

  void _showAddChildDialog() {
    final nameCtrl = TextEditingController();
    final ageCtrl = TextEditingController(text: '10');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Child Profile'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Child Name'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ageCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Age'),
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
              final name = nameCtrl.text.trim();
              final age = int.tryParse(ageCtrl.text) ?? 10;
              if (name.isNotEmpty) {
                Navigator.pop(ctx);
                final api = context.read<ApiService>();
                final newChild = await api.createChild(name, age, 'unspecified');
                if (newChild != null) {
                  await _loadChildren();
                  setState(() => _selectedChild = newChild);
                }
              }
            },
            child: const Text('Add Child'),
          ),
        ],
      ),
    );
  }

  void _showNotificationsSheet() async {
    final api = context.read<ApiService>();
    final notifs = await api.getNotifications();

    if (!mounted) return;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          height: MediaQuery.of(ctx).size.height * 0.7,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Safety & Activity Alerts',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Divider(),
              Expanded(
                child: notifs.isEmpty
                    ? const Center(
                        child: Text(
                          'No alerts received yet.',
                          style: TextStyle(color: AppColors.textMuted),
                        ),
                      )
                    : ListView.builder(
                        itemCount: notifs.length,
                        itemBuilder: (c, i) {
                          final n = notifs[i];
                          return ListTile(
                            leading: CircleAvatar(
                              backgroundColor: AppColors.primaryNavy.withOpacity(0.1),
                              child: const Icon(Icons.notifications_active,
                                  color: AppColors.primaryNavy, size: 20),
                            ),
                            title: Text(n.title,
                                style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text(n.body),
                          );
                        },
                      ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_selectedChild == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('PARENTIQ')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.family_restroom, size: 72, color: AppColors.primaryNavy),
              const SizedBox(height: 16),
              const Text(
                'Welcome to PARENTIQ',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Create your first child profile to begin safety management.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _showAddChildDialog,
                icon: const Icon(Icons.add),
                label: const Text('Add Child Profile'),
              ),
            ],
          ),
        ),
      );
    }

    final child = _selectedChild!;

    final screens = [
      DashboardScreen(
        child: child,
        onNavigateToLocation: () => setState(() => _currentIndex = 1),
        onNavigateToScreenTime: () => setState(() => _currentIndex = 2),
        onNavigateToLive: () => setState(() => _currentIndex = 5),
      ),
      LocationScreen(child: child),
      ScreenTimeScreen(child: child),
      AppsScreen(child: child),
      SafetyScreen(child: child),
      MonitoringScreen(child: child),
      ReportsScreen(child: child),
      SettingsScreen(child: child, onLogout: widget.onLogout),
    ];

    return Scaffold(
      appBar: AppBar(
        title: DropdownButtonHideUnderline(
          child: DropdownButton<String>(
            value: child.id,
            dropdownColor: AppColors.primaryNavy,
            icon: const Icon(Icons.arrow_drop_down, color: Colors.white),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
            items: [
              ..._children.map((c) => DropdownMenuItem(
                    value: c.id,
                    child: Text(c.name),
                  )),
            ],
            onChanged: (id) {
              if (id != null) {
                setState(() {
                  _selectedChild = _children.firstWhere((c) => c.id == id);
                });
              }
            },
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_add_alt_1_outlined),
            tooltip: 'Add Child',
            onPressed: _showAddChildDialog,
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            tooltip: 'Alerts',
            onPressed: _showNotificationsSheet,
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.location_on_outlined),
            selectedIcon: Icon(Icons.location_on),
            label: 'Location',
          ),
          NavigationDestination(
            icon: Icon(Icons.hourglass_empty),
            selectedIcon: Icon(Icons.hourglass_full),
            label: 'Time',
          ),
          NavigationDestination(
            icon: Icon(Icons.apps_outlined),
            selectedIcon: Icon(Icons.apps),
            label: 'Apps',
          ),
          NavigationDestination(
            icon: Icon(Icons.shield_outlined),
            selectedIcon: Icon(Icons.shield),
            label: 'Safety',
          ),
          NavigationDestination(
            icon: Icon(Icons.videocam_outlined),
            selectedIcon: Icon(Icons.videocam),
            label: 'Live',
          ),
          NavigationDestination(
            icon: Icon(Icons.bar_chart_outlined),
            selectedIcon: Icon(Icons.bar_chart),
            label: 'Reports',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}

