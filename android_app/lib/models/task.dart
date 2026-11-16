class ForgeTask {
  final String id;
  final String title;
  final String? description;
  final String priority;
  final String status;
  final String? scheduledDate;
  final String? scheduledTime;
  final int estimatedDurationMinutes;
  final int actualDurationMinutes;
  final String? studyCursorTopicRefId;
  final String? completedAt;

  ForgeTask({
    required this.id,
    required this.title,
    this.description,
    this.priority = 'medium',
    this.status = 'pending',
    this.scheduledDate,
    this.scheduledTime,
    this.estimatedDurationMinutes = 45,
    this.actualDurationMinutes = 0,
    this.studyCursorTopicRefId,
    this.completedAt,
  });

  factory ForgeTask.fromJson(Map<String, dynamic> json) {
    return ForgeTask(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'],
      priority: json['priority'] ?? 'medium',
      status: json['status'] ?? 'pending',
      scheduledDate: json['scheduled_date'],
      scheduledTime: json['scheduled_time'],
      estimatedDurationMinutes: json['estimated_duration_minutes'] ?? 45,
      actualDurationMinutes: json['actual_duration_minutes'] ?? 0,
      studyCursorTopicRefId: json['study_cursor_topic_ref_id'],
      completedAt: json['completed_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'priority': priority,
      'status': status,
      'scheduled_date': scheduledDate,
      'scheduled_time': scheduledTime,
      'estimated_duration_minutes': estimatedDurationMinutes,
      'actual_duration_minutes': actualDurationMinutes,
      'study_cursor_topic_ref_id': studyCursorTopicRefId,
      'completed_at': completedAt,
    };
  }
}
