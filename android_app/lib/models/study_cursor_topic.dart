class StudyCursorTopic {
  final String id;
  final String trackCategory;
  final String? subjectKey;
  final String topicId;
  final String topicTitle;
  final String? clusterName;
  final String? weightage;
  final List<String> subtopics;
  final String statusInStudyCursor;

  StudyCursorTopic({
    required this.id,
    required this.trackCategory,
    this.subjectKey,
    required this.topicId,
    required this.topicTitle,
    this.clusterName,
    this.weightage,
    this.subtopics = const [],
    this.statusInStudyCursor = 'pending',
  });

  factory StudyCursorTopic.fromJson(Map<String, dynamic> json) {
    var rawSub = json['subtopics'] as List? ?? [];
    List<String> subs = rawSub.map((e) => e.toString()).toList();

    return StudyCursorTopic(
      id: json['id'] ?? '',
      trackCategory: json['track_category'] ?? '',
      subjectKey: json['subject_key'],
      topicId: json['topic_id'] ?? '',
      topicTitle: json['topic_title'] ?? '',
      clusterName: json['cluster_name'],
      weightage: json['weightage'],
      subtopics: subs,
      statusInStudyCursor: json['status_in_study_cursor'] ?? 'pending',
    );
  }
}
