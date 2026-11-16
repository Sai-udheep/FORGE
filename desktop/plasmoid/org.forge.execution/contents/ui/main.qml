import QtQuick
import org.kde.plasma.plasmoid

PlasmoidItem {
    id: root

    compactRepresentation: CompactRepresentation {}
    fullRepresentation: FullRepresentation {}

    preferredRepresentation: Plasmoid.fullRepresentation

    // ================= STATE PROPERTIES =================
    property string timerString: "50:00"
    property int remainingSeconds: 3000
    property bool isFocusActive: false
    property string activeFocusId: ""
    property string activeTaskTitle: "Ready for Focus"
    property string activeTopicId: ""
    
    property int streakDays: 0
    property bool studyCursorConnected: false
    property var todayTasks: []
    property int todayTotalCount: 0
    property int todayCompletedCount: 0
    property int completionPct: 0

    property bool showCompletionDialog: false
    property string pendingConfirmTopicId: ""
    property string pendingConfirmTopicTitle: ""

    readonly property string apiBase: "http://127.0.0.1:8000/api/v1"

    // ================= TIMER ENGINE =================
    Timer {
        id: countdownTimer
        interval: 1000
        repeat: true
        running: root.isFocusActive && root.remainingSeconds > 0
        onTriggered: {
            if (root.remainingSeconds > 0) {
                root.remainingSeconds -= 1;
                var mins = Math.floor(root.remainingSeconds / 60);
                var secs = root.remainingSeconds % 60;
                root.timerString = (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
            } else {
                root.isFocusActive = false;
                root.finishFocus();
            }
        }
    }

    // Auto refresh timer every 30 seconds
    Timer {
        interval: 30000
        repeat: true
        running: true
        onTriggered: root.fetchDashboard()
    }

    Component.onCompleted: {
        root.fetchDashboard();
    }

    // ================= REST API CLIENT =================
    function makeRequest(method, endpoint, payload, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open(method, apiBase + endpoint, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        var data = JSON.parse(xhr.responseText);
                        callback(null, data);
                    } catch (e) {
                        callback(e, null);
                    }
                } else {
                    callback("HTTP " + xhr.status + ": " + xhr.responseText, null);
                }
            }
        };
        xhr.send(payload ? JSON.stringify(payload) : null);
    }

    function fetchDashboard() {
        // 1. Fetch Today's Tasks
        makeRequest("GET", "/planner/today", null, function(err, data) {
            if (!err && data) {
                root.todayTasks = data.today_tasks || [];
                root.todayTotalCount = data.metrics.total_tasks || 0;
                root.todayCompletedCount = data.metrics.completed_tasks || 0;
                root.completionPct = data.metrics.completion_percentage || 0;
            }
        });

        // 2. Fetch Analytics & Streak
        makeRequest("GET", "/analytics/dashboard", null, function(err, data) {
            if (!err && data && data.streak) {
                root.streakDays = data.streak.current_streak_days || 0;
            }
        });

        // 3. Fetch Study Cursor Status
        makeRequest("GET", "/integrations/study-cursor/status", null, function(err, data) {
            if (!err && data) {
                root.studyCursorConnected = data.is_connected;
            } else {
                root.studyCursorConnected = false;
            }
        });

        // 4. Check active focus session
        makeRequest("GET", "/focus/active", null, function(err, data) {
            if (!err && data && data.status === "active") {
                root.activeFocusId = data.id;
                root.isFocusActive = true;
            }
        });
    }

    function startFocus(durationMinutes) {
        root.remainingSeconds = durationMinutes * 60;
        var mins = durationMinutes;
        root.timerString = (mins < 10 ? "0" : "") + mins + ":00";
        root.isFocusActive = true;

        makeRequest("POST", "/focus/start", {
            "session_type": durationMinutes === 15 ? "aptitude" : "pomodoro",
            "planned_duration_minutes": durationMinutes
        }, function(err, data) {
            if (!err && data) {
                root.activeFocusId = data.id;
            }
        });
    }

    function pauseFocus() {
        if (!root.activeFocusId) return;
        root.isFocusActive = false;
        makeRequest("POST", "/focus/" + root.activeFocusId + "/pause", null, function(err, data) {
            root.fetchDashboard();
        });
    }

    function finishFocus() {
        if (!root.activeFocusId) return;
        var sessId = root.activeFocusId;
        root.isFocusActive = false;
        root.activeFocusId = "";
        root.timerString = "50:00";
        root.remainingSeconds = 3000;

        makeRequest("POST", "/focus/" + sessId + "/finish", {
            "actual_duration_minutes": 50
        }, function(err, data) {
            root.fetchDashboard();
            // If linked to Study Cursor topic, prompt user explicitly
            if (root.activeTopicId) {
                root.pendingConfirmTopicId = root.activeTopicId;
                root.pendingConfirmTopicTitle = root.activeTaskTitle;
                root.showCompletionDialog = true;
            }
        });
    }

    function completeTask(taskId) {
        makeRequest("POST", "/tasks/" + taskId + "/complete", {}, function(err, data) {
            root.fetchDashboard();
        });
    }

    function importNextTopic() {
        makeRequest("GET", "/integrations/study-cursor/topics?status_filter=pending", null, function(err, topics) {
            if (!err && topics && topics.length > 0) {
                var nextTopic = topics[0];
                makeRequest("POST", "/integrations/study-cursor/import-topic", {
                    "topic_id": nextTopic.topic_id
                }, function(err2, task) {
                    if (!err2) {
                        root.fetchDashboard();
                    }
                });
            }
        });
    }

    function confirmTopicDone() {
        if (!root.pendingConfirmTopicId) return;
        makeRequest("POST", "/integrations/study-cursor/confirm-completion", {
            "topic_id": root.pendingConfirmTopicId,
            "actual_duration_minutes": 50,
            "explicitly_confirmed_by_user": true
        }, function(err, data) {
            root.showCompletionDialog = false;
            root.pendingConfirmTopicId = "";
            root.pendingConfirmTopicTitle = "";
            root.fetchDashboard();
        });
    }

    function dismissCompletionDialog() {
        root.showCompletionDialog = false;
        root.pendingConfirmTopicId = "";
        root.pendingConfirmTopicTitle = "";
    }
}
