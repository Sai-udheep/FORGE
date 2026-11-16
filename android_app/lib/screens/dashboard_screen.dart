import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/glass_theme.dart';
import '../models/task.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _api = ApiService();
  bool _loading = true;
  int _streakDays = 0;
  int _completedTasks = 0;
  int _totalTasks = 0;
  int _focusMinutes = 0;
  double _completionPct = 0.0;
  List<ForgeTask> _tasks = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final dash = await _api.getDashboard();
      final tasks = await _api.getTodayTasks();
      setState(() {
        _streakDays = dash['streak']?['current_streak_days'] ?? 0;
        _completedTasks = dash['today_tasks_completed'] ?? 0;
        _totalTasks = dash['today_tasks_total'] ?? 0;
        _focusMinutes = dash['today_focus_minutes'] ?? 0;
        _completionPct = (dash['today_completion_percentage'] as num?)?.toDouble() ?? 0.0;
        _tasks = tasks;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _toggleTask(ForgeTask task) async {
    try {
      await _api.completeTask(task.id, duration: task.estimatedDurationMinutes);
      _loadData();
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ForgeColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [ForgeColors.flameOrange, ForgeColors.flameDeep],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text('⚡', style: TextStyle(fontSize: 14)),
            ),
            const SizedBox(width: 8),
            const Text(
              'FORGE',
              style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: ForgeColors.flamePrimary.withOpacity(0.18),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: ForgeColors.flamePrimary.withOpacity(0.35)),
            ),
            child: Row(
              children: [
                const Text('🔥 ', style: TextStyle(fontSize: 12)),
                Text(
                  '$_streakDays d Streak',
                  style: const TextStyle(
                    color: ForgeColors.flameOrange,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: ForgeColors.flamePrimary,
        child: _loading
            ? const Center(child: CircularProgressIndicator(color: ForgeColors.flamePrimary))
            : ListView(
                padding: const EdgeInsets.all(16.0),
                children: [
                  // Execution Hero Card
                  GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "TODAY'S EXECUTION",
                          style: TextStyle(
                            color: ForgeColors.textSecondary,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.0,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '$_completedTasks / $_totalTasks Tasks',
                                  style: const TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: ForgeColors.textPrimary,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '$_focusMinutes Mins Focused Today',
                                  style: const TextStyle(
                                    fontSize: 13,
                                    color: ForgeColors.purpleAccent,
                                  ),
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: ForgeColors.electricCyan.withOpacity(0.4),
                                  width: 3,
                                ),
                              ),
                              child: Text(
                                '${_completionPct.toInt()}%',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: ForgeColors.electricCyan,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Quick Action Buttons
                  Row(
                    children: [
                      Expanded(
                        child: GlassCard(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          onTap: () {},
                          child: const Center(
                            child: Text(
                              '⚡ 50m Deep Flow',
                              style: TextStyle(
                                color: ForgeColors.flameOrange,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: GlassCard(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          onTap: () {},
                          child: const Center(
                            child: Text(
                              '🎯 15m Aptitude',
                              style: TextStyle(
                                color: ForgeColors.purpleAccent,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Today's Tasks Header
                  const Text(
                    "TODAY'S AGENDA",
                    style: TextStyle(
                      color: ForgeColors.textSecondary,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.0,
                    ),
                  ),

                  const SizedBox(height: 12),

                  if (_tasks.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 30),
                      child: Center(
                        child: Text(
                          'No tasks scheduled for today.\nImport topics from Study Cursor!',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: ForgeColors.textMuted),
                        ),
                      ),
                    )
                  else
                    ..._tasks.map((task) => Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: GlassCard(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            child: Row(
                              children: [
                                Checkbox(
                                  value: task.status == 'completed',
                                  activeColor: ForgeColors.electricCyan,
                                  checkColor: Colors.black,
                                  onChanged: (_) => _toggleTask(task),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    task.title,
                                    style: TextStyle(
                                      color: task.status == 'completed'
                                          ? ForgeColors.textMuted
                                          : ForgeColors.textPrimary,
                                      decoration: task.status == 'completed'
                                          ? TextDecoration.lineThrough
                                          : null,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: ForgeColors.surface,
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    '${task.estimatedDurationMinutes}m',
                                    style: const TextStyle(
                                      color: ForgeColors.textSecondary,
                                      fontSize: 10,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        )),
                ],
              ),
      ),
    );
  }
}
