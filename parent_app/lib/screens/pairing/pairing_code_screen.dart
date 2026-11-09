import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../models/models.dart';
import '../../services/api_service.dart';

class PairingCodeScreen extends StatefulWidget {
  final ChildModel child;

  const PairingCodeScreen({super.key, required this.child});

  @override
  State<PairingCodeScreen> createState() => _PairingCodeScreenState();
}

class _PairingCodeScreenState extends State<PairingCodeScreen> {
  String? _code;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchPairingCode();
  }

  Future<void> _fetchPairingCode() async {
    setState(() => _isLoading = true);
    final api = context.read<ApiService>();
    final data = await api.initiatePairing(widget.child.id);
    if (mounted) {
      setState(() {
        _code = data?['pairing_code'];
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pair Child Device'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const SizedBox(height: 20),
                  const Icon(
                    Icons.qr_code_scanner,
                    size: 80,
                    color: AppColors.primaryNavy,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Pairing Code for ${widget.child.name}',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Enter this 6-digit code on the PARENTIQ Child Companion application:',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 32),

                  // Large High-Visibility Code Container
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 20),
                    decoration: BoxDecoration(
                      color: AppColors.primaryNavy.withOpacity(0.06),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.primaryNavy.withOpacity(0.2)),
                    ),
                    child: Text(
                      _code != null
                          ? '${_code!.substring(0, 3)} - ${_code!.substring(3)}'
                          : '------',
                      style: const TextStyle(
                        fontSize: 38,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 6,
                        color: AppColors.primaryNavy,
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.timer_outlined, size: 16, color: AppColors.warning),
                      SizedBox(width: 6),
                      Text(
                        'Code expires in 15 minutes',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.warning,
                        ),
                      ),
                    ],
                  ),

                  const Spacer(),

                  // Steps walkthrough
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.cardBorder),
                    ),
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Instructions:',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        SizedBox(height: 8),
                        Text('1. Install PARENTIQ Child App on child device.'),
                        SizedBox(height: 4),
                        Text('2. Open the app and tap "Enter Pairing Code".'),
                        SizedBox(height: 4),
                        Text('3. Enter the 6-digit code shown above.'),
                        SizedBox(height: 4),
                        Text('4. Grant required accessibility and location permissions.'),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: _fetchPairingCode,
                      child: const Text('Generate New Code'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

