import QtQuick
import QtQuick.Layouts

Rectangle {
    id: cardRoot
    radius: 14
    color: Qt.rgba(1.0, 1.0, 1.0, 0.07) // Frosted translucent glass inset
    border.color: Qt.rgba(1.0, 1.0, 1.0, 0.15)  // Specular frosted border
    border.width: 1

    // Subtle macOS specular reflection along top edge
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        radius: cardRoot.radius
        color: Qt.rgba(1.0, 1.0, 1.0, 0.25)
    }
}
