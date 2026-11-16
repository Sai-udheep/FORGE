import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    radius: 14
    color: Qt.rgba(0.086, 0.094, 0.125, 0.72) // Translucent Obsidian Glass
    border.color: Qt.rgba(1.0, 1.0, 1.0, 0.12)  // Specular frosted border
    border.width: 1

    // Subtle macOS specular reflection along top edge
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        radius: root.radius
        color: Qt.rgba(1.0, 1.0, 1.0, 0.22)
    }
}
