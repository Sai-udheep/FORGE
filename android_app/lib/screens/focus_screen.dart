import 'dart:async';
import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/glass_theme.dart';
import '../services/api_service.dart';
import '../models/study_cursor_topic.dart';

class FocusScreen extends StatefulWidget {
  const FocusScreen({Key? key}) : super(key: key);

  @override
  State<FocusScreen> createState() => _FocusScreenState();
}

class _FocusScreenState extends State<FocusScreen> {
  final ApiService _api = ApiService();
  Timer? _timer;
  int _totalSeconds = 3000; // 50 mins
  int _remainingSeconds = 3000;
  bool _isRunning = false;
  String? _activeSessionId;

  StudyCursorTopic? _selectedTopic;
  List<StudyCursorTopic> _topics = [];

  @override
  void initState() {
    super.initState();
    _loadTopics();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _loadTopics() async {
    try {
      final topics = await _api.getStudyCursorTopics();
      if (mounted) setState(() => _topics = topics);
    } catch (_) {}
  }

  void _setDuration(int minutes) {
    if (_isRunning) return;
    setState(() {
      _totalSeconds = minutes * 60;
      _remainingSeconds = _totalSeconds;
    });
  }

  void _toggleTimer() async {
    if (_isRunning) {
      _timer?.cancel();
      setState(() => _isRunning = false);
    } else {
      setState(() => _isRunning = true);
      try {
        final sess = await _api.startFocus(
          _totalSeconds ~/ 60,
          topicRefId: _selectedTopic?.id,
        );
        _activeSessionId = sess.id;
      } catch (_) {}

      _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
        if (_remainingSeconds > 0) {
          setState(() => _remainingSeconds--);
        } else {
          _timer?.cancel();
          _finishSession();
        }
      });
    }
  }

  void _finishSession() async {
    _timer?.cancel();
    final elapsedMinutes = (_totalSeconds - _remainingSeconds) ~/ 60;

    if (_activeSessionId != null) {
      try {
        await _api.finishFocus(_activeSessionId!, elapsedMinutes);
      } catch (_) {}
    }

    setState(() {
      _isRunning = false;
      _remainingSeconds = _totalSeconds;
    });

    if (_selectedTopic != null) {
      _showCompletionConfirmationDialog(_selectedTopic!, elapsedMinutes);
    }
  }

  void _showCompletionConfirmationDialog(StudyCursorTopic topic, int elapsedMinutes) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: ForgeColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: ForgeColors.glassBorder),
        ),
        title: const Text(
          'Confirm Topic Completion',
          style: TextStyle(color: ForgeColors.flameOrange, fontWeight: FontWeight.bold),
        ),
        content: Text(
          'You just finished $elapsedMinutes minutes on:\n"${topic.topicTitle}".\n\nDid you finish this topic in Study Cursor?',
          style: const TextStyle(color: ForgeColors.textPrimary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('No, Not Yet', style: TextStyle(color: ForgeColors.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: ForgeColors.flamePrimary,
              foregroundColor: Colors.white,
            ),
            onPressed: () async {
              Navigator.pop(ctx);
              try {
                await _api.confirmTopicCompletion(topic.topicId, elapsedMinutes);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('✅ Topic completed and synced with Study Cursor!')),
                );
                _loadTopics();
              } catch (_) {}
            },
            child: const Text('Yes, Mark Complete'),
          ),
        ],
      ),
    );
  }

  String _formatTime(int sec) {
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    final progress = _totalSeconds > 0 ? (_totalSeconds - _remainingSeconds) / _totalSeconds : 0.0;

    return Scaffold(
      backgroundColor: ForgeColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('FOCUS SITTING', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            // Duration Selectors
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _durationChip(50, '50m Deep Work'),
                const SizedBox(width: 10),
                _durationChip(25, '25m Sprint'),
                const SizedBox(width: 10),
                _durationChip(15, '15m Aptitude'),
              ],
            ),

            const Spacer(),

            // Circular macOS Frosted Glass Timer
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 240,
                  height: 240,
                  child: CircularProgressIndicator(
                    value: progress,
                    strokeWidth: 8,
                    backgroundColor: ForgeColors.surface,
                    valueColor: const AlwaysStoppedAnimation<Color>(ForgeColors.flamePrimary),
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _formatTime(_remainingSeconds),
                      style: const TextStyle(
                        fontSize: 54,
                        fontWeight: FontWeight.bold,
                        fontFamily: 'monospace',
                        color: ForgeColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _selectedTopic != null ? _selectedTopic!.topicTitle : 'General Focus Sitting',
                      textAlign: TextAlign.center,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: ForgeColors.purpleAccent,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),

            const Spacer(),

            // Topic Selector Dropdown
            GlassCard(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<StudyCursorTopic>(
                  isExpanded: true,
                  dropdownColor: ForgeColors.surface,
                  value: _selectedTopic,
                  hint: const Text(
                    'Link to Study Cursor Topic (Optional)',
                    style: TextStyle(color: ForgeColors.textMuted, fontSize: 13),
                  ),
                  items: _topics.map((t) {
                    return DropdownMenuItem(
                      value: t,
                      child: Text(
                        '[${t.trackCategory.toUpperCase()}] ${t.topicTitle}',
                        style: const TextStyle(color: ForgeColors.textPrimary, fontSize: 13),
                        overflow: TextOverflow.ellipsis,
                      ),
                    );
                  }).toList(),
                  onChanged: _isRunning ? null : (val) => setState(() => _selectedTopic = val),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Control Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: ForgeColors.flamePrimary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    onPressed: _toggleTimer,
                    child: Text(
                      _isRunning ? 'PAUSE' : 'START FOCUS',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ),
                ),
                if (_isRunning) ...[
                  const SizedBox(width: 12),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: ForgeColors.surface,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    onPressed: _finishSession,
                    child: const Text('FINISH'),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _durationChip(int mins, String label) {
    final selected = (_totalSeconds ~/ 60) == mins;
    return GestureDetector(
      onTap: () => _setDuration(mins),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? ForgeColors.flamePrimary.withOpacity(0.2) : ForgeColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? ForgeColors.flamePrimary : ForgeColors.glassBorder,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? ForgeColors.flameOrange : ForgeColors.textSecondary,
            fontWeight: selected ? FontWeight.bold : FontWeight.normal,
            fontSize: 12,
          ),
        ),
      ),
    );
  }
}
