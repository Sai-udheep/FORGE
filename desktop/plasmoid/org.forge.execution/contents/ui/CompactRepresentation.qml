import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.plasma.plasmoid

Item {
    id: compactRoot
    Layout.minimumWidth: timerText.visible ? 76 : 36
    Layout.minimumHeight: 28

    RowLayout {
        anchors.centerIn: parent
        spacing: 6

        // Flame Indicator
        Rectangle {
            width: 12
            height: 12
            radius: 6
            color: root && root.isFocusActive ? "#FF6B35" : "#8B5CF6"
            
            SequentialAnimation on opacity {
                running: root ? root.isFocusActive : false
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 0.4; duration: 800 }
                NumberAnimation { from: 0.4; to: 1.0; duration: 800 }
            }
        }

        QQC2.Label {
            id: timerText
            text: root ? root.timerString : "FORGE"
            font.bold: true
            font.pixelSize: 12
            color: root && root.isFocusActive ? "#FF6B35" : "#FFFFFF"
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: Plasmoid.expanded = !Plasmoid.expanded
    }
}
