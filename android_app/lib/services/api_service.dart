import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/task.dart';
import '../models/focus_session.dart';
import '../models/study_cursor_topic.dart';

class ApiService {
  static const String defaultUrl = "http://10.0.2.2:8000/api/v1"; // Android emulator to host
  static const String keyBaseUrl = "forge_base_url";

  Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(keyBaseUrl) ?? defaultUrl;
  }

  Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyBaseUrl, url.trim().replaceAll(RegExp(r'/+$'), ''));
  }

  Future<Map<String, dynamic>> getDashboard() async {
    final baseUrl = await getBaseUrl();
    final resp = await http.get(Uri.parse('$baseUrl/analytics/dashboard'));
    if (resp.statusCode == 200) {
      return jsonDecode(resp.body);
    }
    throw Exception('Failed to load dashboard: ${resp.body}');
  }

  Future<List<ForgeTask>> getTodayTasks() async {
    final baseUrl = await getBaseUrl();
    final resp = await http.get(Uri.parse('$baseUrl/planner/today'));
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      final list = data['today_tasks'] as List? ?? [];
      return list.map((e) => ForgeTask.fromJson(e)).toList();
    }
    throw Exception('Failed to load today planner: ${resp.body}');
  }

  Future<ForgeTask> completeTask(String taskId, {int duration = 45}) async {
    final baseUrl = await getBaseUrl();
    final resp = await http.post(
      Uri.parse('$baseUrl/tasks/$taskId/complete'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'actual_duration_minutes': duration}),
    );
    if (resp.statusCode == 200) {
      return ForgeTask.fromJson(jsonDecode(resp.body));
    }
    throw Exception('Failed to complete task');
  }

  Future<ForgeFocusSession> startFocus(int durationMinutes, {String? taskId, String? topicRefId}) async {
    final baseUrl = await getBaseUrl();
    final resp = await http.post(
      Uri.parse('$baseUrl/focus/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_type': durationMinutes == 15 ? 'aptitude' : 'pomodoro',
        'planned_duration_minutes': durationMinutes,
        'task_id': taskId,
        'study_cursor_topic_ref_id': topicRefId,
      }),
    );
    if (resp.statusCode == 201) {
      return ForgeFocusSession.fromJson(jsonDecode(resp.body));
    }
    throw Exception('Failed to start focus session');
  }

  Future<void> finishFocus(String sessionId, int actualMinutes) async {
    final baseUrl = await getBaseUrl();
    await http.post(
      Uri.parse('$baseUrl/focus/$sessionId/finish'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'actual_duration_minutes': actualMinutes}),
    );
  }

  Future<List<StudyCursorTopic>> getStudyCursorTopics({String? track}) async {
    final baseUrl = await getBaseUrl();
    var uri = '$baseUrl/integrations/study-cursor/topics?status_filter=pending';
    if (track != null) uri += '&track_category=$track';
    final resp = await http.get(Uri.parse(uri));
    if (resp.statusCode == 200) {
      final list = jsonDecode(resp.body) as List? ?? [];
      return list.map((e) => StudyCursorTopic.fromJson(e)).toList();
    }
    return [];
  }

  Future<void> importTopic(String topicId) async {
    final baseUrl = await getBaseUrl();
    await http.post(
      Uri.parse('$baseUrl/integrations/study-cursor/import-topic'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic_id': topicId}),
    );
  }

  Future<void> confirmTopicCompletion(String topicId, int durationMinutes) async {
    final baseUrl = await getBaseUrl();
    final resp = await http.post(
      Uri.parse('$baseUrl/integrations/study-cursor/confirm-completion'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'topic_id': topicId,
        'actual_duration_minutes': durationMinutes,
        'explicitly_confirmed_by_user': true,
      }),
    );
    if (resp.statusCode != 200) {
      throw Exception('Failed to confirm topic completion: ${resp.body}');
    }
  }
}
