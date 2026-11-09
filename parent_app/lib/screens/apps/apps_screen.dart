import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class AppsScreen extends StatefulWidget {
  final ChildModel child;

  const AppsScreen({super.key, required this.child});

  @override
  State<AppsScreen> createState() => _AppsScreenState();
}

class _AppsScreenState extends State<AppsScreen> {
  List<InstalledAppModel> _apps = [];
  List<AppUsageModel> _usages = [];
  final Map<String, bool> _blockedMap = {};
  String _searchQuery = '';
  String _selectedCategory = 'All';
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAppData();
  }

  Future<void> _loadAppData() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final apps = await api.getInstalledApps(widget.child.id);
    final usages = await api.getAppUsages(widget.child.id);
    if (mounted) {
      setState(() {
        _apps = apps;
        _usages = usages;
        _isLoading = false;
      });
    }
  }

  Future<void> _toggleBlockApp(InstalledAppModel app, bool isBlocked) async {
    final api = context.read<ApiService>();
    setState(() {
      _blockedMap[app.packageName] = isBlocked;
    });
    await api.setAppRestriction(
      widget.child.id,
      app.packageName,
      app.appName,
      isBlocked,
    );
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isBlocked
                ? '${app.appName} is now blocked on child device.'
                : '${app.appName} is now unblocked.',
          ),
          backgroundColor: isBlocked ? AppColors.danger : AppColors.success,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final filteredApps = _apps.where((app) {
      final matchesSearch = app.appName.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          app.packageName.toLowerCase().contains(_searchQuery.toLowerCase());
      final matchesCategory = _selectedCategory == 'All' || app.category == _selectedCategory;
      return matchesSearch && matchesCategory;
    }).toList();

    final categories = ['All', 'Games', 'Social', 'Education', 'Entertainment', 'Other'];

    return RefreshIndicator(
      onRefresh: _loadAppData,
      child: Column(
        children: [
          // Search & Filter Header
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                TextField(
                  decoration: InputDecoration(
                    hintText: 'Search installed applications...',
                    prefixIcon: const Icon(Icons.search),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppColors.cardBorder),
                    ),
                  ),
                  onChanged: (val) => setState(() => _searchQuery = val),
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: categories.map((cat) {
                      final isSelected = _selectedCategory == cat;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: Text(cat),
                          selected: isSelected,
                          selectedColor: AppColors.primaryNavy.withOpacity(0.15),
                          onSelected: (val) {
                            setState(() => _selectedCategory = cat);
                          },
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          // App Inventory List
          Expanded(
            child: filteredApps.isEmpty
                ? const Center(
                    child: Text(
                      'No applications match your filter.',
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: filteredApps.length,
                    itemBuilder: (ctx, i) {
                      final app = filteredApps[i];
                      final isBlocked = _blockedMap[app.packageName] ?? false;
                      final usage = _usages.firstWhere(
                        (u) => u.packageName == app.packageName,
                        orElse: () => AppUsageModel(
                          packageName: '',
                          appName: '',
                          category: '',
                          foregroundSeconds: 0,
                          launchCount: 0,
                        ),
                      );

                      return Card(
                        child: ListTile(
                          leading: Container(
                            width: 44,
                            height: 44,
                            decoration: BoxDecoration(
                              color: isBlocked
                                  ? AppColors.danger.withOpacity(0.1)
                                  : AppColors.secondaryRoyal.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Icon(
                              Icons.android,
                              color: isBlocked ? AppColors.danger : AppColors.secondaryRoyal,
                            ),
                          ),
                          title: Text(
                            app.appName,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              decoration: isBlocked ? TextDecoration.lineThrough : null,
                            ),
                          ),
                          subtitle: Text(
                            '${app.category} • Today: ${usage.foregroundSeconds ~/ 60}m used',
                            style: const TextStyle(fontSize: 12),
                          ),
                          trailing: Switch(
                            value: !isBlocked,
                            activeColor: AppColors.success,
                            inactiveThumbColor: AppColors.danger,
                            onChanged: (val) => _toggleBlockApp(app, !val),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

