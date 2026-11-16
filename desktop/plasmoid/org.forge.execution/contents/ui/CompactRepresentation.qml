import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.core as PlasmaCore

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
            color: plasmoid.rootItem ? (plasmoid.rootItem.isFocusActive ? "#FF6B35" : "#8B5CF6") : "#FF6B35"
            
            SequentialAnimation on opacity {
                running: plasmoid.rootItem ? plasmoid.rootItem.isFocusActive : false
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 0.4; duration: 800 }
                NumberAnimation { from: 0.4; to: 1.0; duration: 800 }
            }
        }

        PlasmaComponents.Label {
            id: timerText
            text: plasmoid.rootItem ? plasmoid.rootItem.timerString : "FORGE"
            font.bold: true
            font.pixelSize: 12
            color: plasmoid.rootItem && plasmoid.rootItem.isFocusActive ? "#FF6B35" : "#FFFFFF"
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: plasmoid.expanded = !plasmoid.expanded
    }
}
