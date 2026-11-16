import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/glass_theme.dart';
import '../services/api_service.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({Key? key}) : super(key: key);

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  final ApiService _api = ApiService();
  bool _loading = true;
  Map<String, dynamic>? _data;

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    try {
      final res = await _api.getDashboard();
      if (mounted) setState(() { _data = res; _loading = false; });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final streak = _data?['streak']?['current_streak_days'] ?? 0;
    final weekly = _data?['weekly_velocity'] as List? ?? [];

    return Scaffold(
      backgroundColor: ForgeColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('PRODUCTIVITY ANALYTICS', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: ForgeColors.flamePrimary))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                GlassCard(
                  child: Row(
                    children: [
                      const Text('🔥', style: TextStyle(fontSize: 32)),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '$streak Day Consistency Streak',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: ForgeColors.flameOrange,
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'Active daily habit loop maintained',
                            style: TextStyle(color: ForgeColors.textSecondary, fontSize: 12),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                const Text(
                  '7-DAY VELOCITY (PLANNED VS ACTUAL)',
                  style: TextStyle(
                    color: ForgeColors.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.0,
                  ),
                ),
                const SizedBox(height: 12),

                ...weekly.map((w) {
                  final date = w['date'] ?? '';
                  final planned = w['planned_minutes'] ?? 0;
                  final actual = w['actual_minutes'] ?? 0;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: GlassCard(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(date, style: const TextStyle(color: ForgeColors.textPrimary)),
                          Row(
                            children: [
                              Text(
                                'Planned: ${planned}m',
                                style: const TextStyle(color: ForgeColors.textMuted, fontSize: 12),
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Actual: ${actual}m',
                                style: const TextStyle(
                                  color: ForgeColors.electricCyan,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                }),
              ],
            ),
    );
  }
}
