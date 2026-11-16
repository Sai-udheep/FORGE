import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import "components"

Item {
    id: fullRoot
    implicitWidth: 380
    implicitHeight: 560

    LiquidGlass {
        id: glass
        anchors.fill: parent
        radius: 28
        roundness: 7.0
        refractThickness: 35
        refractIOR: 1.7
        refractScale: 65
        tint: "#000000"
        tintAlpha: 0.28
        chromaStrength: 0.30
        specStrength: 0.70
        blurRadius: 6
        fallbackOpacity: 0.50
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        // ================= HEADER =================
        RowLayout {
            Layout.fillWidth: true

            // Flame Emblem
            Rectangle {
                width: 26
                height: 26
                radius: 7
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#FF8A48" }
                    GradientStop { position: 1.0; color: "#F74C1E" }
                }
                QQC2.Label {
                    anchors.centerIn: parent
                    text: "⚡"
                    font.pixelSize: 13
                }
            }

            ColumnLayout {
                spacing: 0
                QQC2.Label {
                    text: "FORGE 2.0"
                    font.bold: true
                    font.pixelSize: 14
                    color: "#FFFFFF"
                }
                QQC2.Label {
                    text: "PLAN • FOCUS • TRACK • GROW"
                    font.pixelSize: 8
                    color: Qt.rgba(1, 1, 1, 0.5)
                }
            }

            Item { Layout.fillWidth: true }

            // Streak Pill
            Rectangle {
                height: 22
                width: streakLabel.implicitWidth + 14
                radius: 11
                color: Qt.rgba(1.0, 0.42, 0.21, 0.18)
                border.color: Qt.rgba(1.0, 0.42, 0.21, 0.35)

                QQC2.Label {
                    id: streakLabel
                    anchors.centerIn: parent
                    text: "🔥 " + (root ? root.streakDays : "0") + "d Streak"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#FF8A48"
                }
            }

            // Refresh Button
            QQC2.ToolButton {
                text: "⟳"
                onClicked: if (root) root.fetchDashboard()
            }
        }

        // ================= FOCUS SESSION HERO CARD =================
        GlassCard {
            Layout.fillWidth: true
            implicitHeight: 160

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    QQC2.Label {
                        text: root && root.isFocusActive ? "ACTIVE FOCUS SESSION" : "FOCUS TIMER"
                        font.pixelSize: 9
                        font.bold: true
                        color: root && root.isFocusActive ? "#FF6B35" : Qt.rgba(1, 1, 1, 0.5)
                    }
                    Item { Layout.fillWidth: true }
                    QQC2.Label {
                        text: root ? root.activeTaskTitle : "Deep Focus Sitting"
                        font.pixelSize: 10
                        color: "#8B5CF6"
                        elide: Text.ElideRight
                        Layout.maximumWidth: 180
                    }
                }

                // Big Timer Display
                QQC2.Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: root ? root.timerString : "50:00"
                    font.pixelSize: 42
                    font.bold: true
                    font.family: "Monospace"
                    color: root && root.isFocusActive ? "#FF6B35" : "#FFFFFF"
                }

                // Timer Controls
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 12

                    QQC2.Button {
                        text: root && root.isFocusActive ? "Pause" : "Start Focus"
                        highlighted: true
                        onClicked: {
                            if (root) {
                                if (root.isFocusActive) root.pauseFocus();
                                else root.startFocus(50);
                            }
                        }
                    }

                    QQC2.Button {
                        text: "Finish Sitting"
                        enabled: root && root.activeFocusId !== ""
                        onClicked: {
                            if (root) root.finishFocus();
                        }
                    }

                    QQC2.Button {
                        text: "15m Aptitude"
                        onClicked: {
                            if (root) root.startFocus(15);
                        }
                    }
                }
            }
        }

        // ================= TODAY'S TASKS LIST =================
        GlassCard {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    QQC2.Label {
                        text: "TODAY'S EXECUTION (" + (root ? root.todayCompletedCount : 0) + "/" + (root ? root.todayTotalCount : 0) + ")"
                        font.pixelSize: 10
                        font.bold: true
                        color: Qt.rgba(1, 1, 1, 0.6)
                    }
                    Item { Layout.fillWidth: true }
                    QQC2.Label {
                        text: (root ? root.completionPct : "0") + "%"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#06B6D4"
                    }
                }

                ListView {
                    id: taskList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: root ? root.todayTasks : []
                    spacing: 6

                    delegate: Rectangle {
                        width: taskList.width
                        height: 38
                        radius: 8
                        color: Qt.rgba(1.0, 1.0, 1.0, 0.06)
                        border.color: modelData.status === "completed" ? Qt.rgba(0.06, 0.71, 0.83, 0.4) : Qt.rgba(1, 1, 1, 0.10)

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8

                            QQC2.CheckBox {
                                checked: modelData.status === "completed"
                                onToggled: {
                                    if (root && modelData.id) {
                                        root.completeTask(modelData.id);
                                    }
                                }
                            }

                            QQC2.Label {
                                Layout.fillWidth: true
                                text: modelData.title
                                font.pixelSize: 11
                                font.strikeout: modelData.status === "completed"
                                color: modelData.status === "completed" ? Qt.rgba(1, 1, 1, 0.4) : "#FFFFFF"
                                elide: Text.ElideRight
                            }

                            QQC2.Label {
                                text: (modelData.estimated_duration_minutes || 45) + "m"
                                font.pixelSize: 9
                                color: Qt.rgba(1, 1, 1, 0.4)
                            }
                        }
                    }
                }
            }
        }

        // ================= STUDY CURSOR SYNC FOOTER =================
        RowLayout {
            Layout.fillWidth: true

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: root && root.studyCursorConnected ? "#10B981" : "#EF4444"
            }

            QQC2.Label {
                text: root && root.studyCursorConnected ? "Study Cursor Synced (131 Topics)" : "Study Cursor Disconnected"
                font.pixelSize: 9
                color: Qt.rgba(1, 1, 1, 0.5)
            }

            Item { Layout.fillWidth: true }

            QQC2.Button {
                text: "Import Topic"
                onClicked: if (root) root.importNextTopic()
            }
        }
    }

    // ================= EXPLICIT COMPLETION MODAL =================
    Rectangle {
        id: confirmationModal
        anchors.fill: parent
        radius: 18
        color: Qt.rgba(0, 0, 0, 0.82)
        visible: root ? root.showCompletionDialog : false

        GlassCard {
            anchors.centerIn: parent
            width: parent.width - 40
            height: 200

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                QQC2.Label {
                    text: "Confirm Topic Completion"
                    font.bold: true
                    font.pixelSize: 14
                    color: "#FF6B35"
                }

                QQC2.Label {
                    Layout.fillWidth: true
                    text: "You just finished a focus sitting for:\n" + (root ? root.pendingConfirmTopicTitle : "") + "\n\nDid you finish this topic in Study Cursor?"
                    font.pixelSize: 11
                    wrapMode: Text.Wrap
                    color: "#FFFFFF"
                }

                Item { Layout.fillHeight: true }

                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10

                    QQC2.Button {
                        text: "No, Not Yet"
                        onClicked: if (root) root.dismissCompletionDialog()
                    }

                    QQC2.Button {
                        text: "Yes, Mark Complete"
                        highlighted: true
                        onClicked: if (root) root.confirmTopicDone()
                    }
                }
            }
        }
    }
}
