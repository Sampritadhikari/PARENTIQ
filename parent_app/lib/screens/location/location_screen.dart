import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class LocationScreen extends StatefulWidget {
  final ChildModel child;

  const LocationScreen({super.key, required this.child});

  @override
  State<LocationScreen> createState() => _LocationScreenState();
}

class _LocationScreenState extends State<LocationScreen> {
  List<LocationLogModel> _history = [];
  List<GeofenceModel> _geofences = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadLocationData();
  }

  Future<void> _loadLocationData() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final history = await api.getLocationHistory(widget.child.id);
    final geofences = await api.getGeofences(widget.child.id);
    if (mounted) {
      setState(() {
        _history = history;
        _geofences = geofences;
        _isLoading = false;
      });
    }
  }

  void _showAddGeofenceDialog() {
    final nameCtrl = TextEditingController();
    final latCtrl = TextEditingController(
      text: _history.isNotEmpty ? _history.first.latitude.toString() : '37.7749',
    );
    final lonCtrl = TextEditingController(
      text: _history.isNotEmpty ? _history.first.longitude.toString() : '-122.4194',
    );
    double radius = 250.0;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(builder: (ctx, setDialogState) {
          return Padding(
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 20,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Create New Safe Zone',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Zone Name (e.g., Home, Elementary School)',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: latCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Latitude',
                          border: OutlineInputBorder(),
                        ),
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: TextField(
                        controller: lonCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Longitude',
                          border: OutlineInputBorder(),
                        ),
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text('Radius: ${radius.round()} meters'),
                Slider(
                  value: radius,
                  min: 50,
                  max: 2000,
                  divisions: 39,
                  label: '${radius.round()}m',
                  activeColor: AppColors.primaryNavy,
                  onChanged: (val) => setDialogState(() => radius = val),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () async {
                      final lat = double.tryParse(latCtrl.text) ?? 37.7749;
                      final lon = double.tryParse(lonCtrl.text) ?? -122.4194;
                      final name = nameCtrl.text.trim();
                      if (name.isNotEmpty) {
                        Navigator.pop(ctx);
                        final api = context.read<ApiService>();
                        await api.createGeofence(widget.child.id, name, lat, lon, radius);
                        _loadLocationData();
                      }
                    },
                    child: const Text('Save Safe Zone'),
                  ),
                ),
              ],
            ),
          );
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final latest = _history.isNotEmpty ? _history.first : null;

    return RefreshIndicator(
      onRefresh: _loadLocationData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Live Map Display Card
          Card(
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                Container(
                  height: 220,
                  width: double.infinity,
                  decoration: const BoxDecoration(
                    color: Color(0xFFE2E8F0),
                    image: DecorationImage(
                      image: NetworkImage(
                          'https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&w=800&q=80'),
                      fit: BoxFit.cover,
                    ),
                  ),
                  child: Stack(
                    children: [
                      Container(color: Colors.black.withOpacity(0.25)),
                      Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: AppColors.primaryNavy,
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.3),
                                    blurRadius: 10,
                                  ),
                                ],
                              ),
                              child: const Icon(
                                Icons.person_pin_circle,
                                color: Colors.white,
                                size: 36,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                widget.child.name,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                  color: AppColors.primaryNavy,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      Positioned(
                        bottom: 12,
                        right: 12,
                        child: FloatingActionButton.small(
                          onPressed: _loadLocationData,
                          backgroundColor: Colors.white,
                          child: const Icon(Icons.my_location,
                              color: AppColors.primaryNavy),
                        ),
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              latest?.address ??
                                  (latest != null
                                      ? 'Coordinates: ${latest.latitude.toStringAsFixed(4)}, ${latest.longitude.toStringAsFixed(4)}'
                                      : 'No coordinates logged yet'),
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              latest != null
                                  ? 'Updated: ${DateFormat.jm().format(latest.recordedAt.toLocal())} • Accuracy: ${latest.accuracy?.round() ?? 5}m'
                                  : 'Waiting for device GPS synchronization...',
                              style: const TextStyle(
                                fontSize: 12,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.gps_fixed, color: AppColors.success),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Safe Zones & Geofencing Header
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Safe Zones (Geofences)',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              TextButton.icon(
                onPressed: _showAddGeofenceDialog,
                icon: const Icon(Icons.add, size: 18),
                label: const Text('Add Zone'),
              ),
            ],
          ),
          const SizedBox(height: 8),

          if (_geofences.isEmpty)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Icon(Icons.shield_outlined,
                        color: AppColors.textMuted, size: 32),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text(
                        'No safe zones defined yet. Add Home or School to receive arrival & departure alerts.',
                        style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                      ),
                    ),
                    ElevatedButton(
                      onPressed: _showAddGeofenceDialog,
                      child: const Text('Add'),
                    ),
                  ],
                ),
              ),
            )
          else
            ..._geofences.map((gf) {
              return Card(
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: AppColors.accentCyanLight,
                    child: Icon(Icons.home, color: AppColors.primaryNavy),
                  ),
                  title: Text(gf.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('Radius: ${gf.radiusMeters.round()}m • Entry & Exit Alerts On'),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppColors.danger),
                    onPressed: () async {
                      final api = context.read<ApiService>();
                      await api.deleteGeofence(gf.id);
                      _loadLocationData();
                    },
                  ),
                ),
              );
            }),

          // Location History Timeline
          const SizedBox(height: 16),
          const Text(
            'Location History Timeline',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          if (_history.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Center(
                  child: Text(
                    'No location history points recorded for today.',
                    style: TextStyle(color: AppColors.textMuted),
                  ),
                ),
              ),
            )
          else
            Card(
              child: ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _history.length,
                separatorBuilder: (ctx, i) => const Divider(height: 1),
                itemBuilder: (ctx, i) {
                  final item = _history[i];
                  return ListTile(
                    leading: const Icon(Icons.place_outlined,
                        color: AppColors.secondaryRoyal),
                    title: Text(
                      item.address ??
                          '${item.latitude.toStringAsFixed(5)}, ${item.longitude.toStringAsFixed(5)}',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                    ),
                    subtitle: Text(
                      '${DateFormat.jm().format(item.recordedAt.toLocal())} • Speed: ${item.speed?.toStringAsFixed(1) ?? '0.0'} m/s',
                      style: const TextStyle(fontSize: 12),
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

