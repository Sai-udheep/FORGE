import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/glass_theme.dart';
import '../services/api_service.dart';
import '../models/task.dart';
import '../models/study_cursor_topic.dart';

class PlannerScreen extends StatefulWidget {
  const PlannerScreen({Key? key}) : super(key: key);

  @override
  State<PlannerScreen> createState() => _PlannerScreenState();
}

class _PlannerScreenState extends State<PlannerScreen> {
  final ApiService _api = ApiService();
  List<ForgeTask> _tasks = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPlanner();
  }

  Future<void> _loadPlanner() async {
    setState(() => _loading = true);
    try {
      final tasks = await _api.getTodayTasks();
      setState(() {
        _tasks = tasks;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  void _showImportSheet() async {
    final topics = await _api.getStudyCursorTopics();
    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      backgroundColor: ForgeColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Import from Study Cursor',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: ForgeColors.textPrimary,
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: ListView.builder(
                  itemCount: topics.length,
                  itemBuilder: (ctx, i) {
                    final t = topics[i];
                    return ListTile(
                      title: Text(
                        t.topicTitle,
                        style: const TextStyle(color: ForgeColors.textPrimary, fontSize: 13),
                      ),
                      subtitle: Text(
                        '${t.trackCategory.toUpperCase()} • ${t.weightage ?? ""}',
                        style: const TextStyle(color: ForgeColors.textSecondary, fontSize: 11),
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.add_circle, color: ForgeColors.flamePrimary),
                        onPressed: () async {
                          Navigator.pop(ctx);
                          await _api.importTopic(t.topicId);
                          _loadPlanner();
                        },
                      ),
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
    return Scaffold(
      backgroundColor: ForgeColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('DAILY PLANNER', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.add, color: ForgeColors.flamePrimary),
            onPressed: _showImportSheet,
          )
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: ForgeColors.flamePrimary))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _tasks.length,
              itemBuilder: (ctx, idx) {
                final task = _tasks[idx];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                task.title,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: ForgeColors.textPrimary,
                                ),
                              ),
                            ),
                            Text(
                              '${task.estimatedDurationMinutes}m',
                              style: const TextStyle(color: ForgeColors.purpleAccent, fontSize: 12),
                            ),
                          ],
                        ),
                        if (task.description != null && task.description!.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(
                            task.description!,
                            style: const TextStyle(color: ForgeColors.textSecondary, fontSize: 12),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
