class ForgeFocusSession {
  final String id;
  final String? taskId;
  final String? studyCursorTopicRefId;
  final String sessionType;
  final String startTime;
  final String? endTime;
  final int plannedDurationMinutes;
  final int actualDurationMinutes;
  final String status;
  final String? notes;

  ForgeFocusSession({
    required this.id,
    this.taskId,
    this.studyCursorTopicRefId,
    this.sessionType = 'pomodoro',
    required this.startTime,
    this.endTime,
    this.plannedDurationMinutes = 50,
    this.actualDurationMinutes = 0,
    this.status = 'active',
    this.notes,
  });

  factory ForgeFocusSession.fromJson(Map<String, dynamic> json) {
    return ForgeFocusSession(
      id: json['id'] ?? '',
      taskId: json['task_id'],
      studyCursorTopicRefId: json['study_cursor_topic_ref_id'],
      sessionType: json['session_type'] ?? 'pomodoro',
      startTime: json['start_time'] ?? '',
      endTime: json['end_time'],
      plannedDurationMinutes: json['planned_duration_minutes'] ?? 50,
      actualDurationMinutes: json['actual_duration_minutes'] ?? 0,
      status: json['status'] ?? 'active',
      notes: json['notes'],
    );
  }
}
