import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: Theme.background
    anchors.fill: parent

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20
        width: parent.width * 0.85

        Label {
            text: "Admin Dashboard"
            font.pixelSize: 24
            color: Theme.text
            Layout.alignment: Qt.AlignHCenter
        }

        // Send alert
        Label { text: "System Alert:"; color: Theme.text }
        TextArea {
            id: alertText
            placeholderText: "Enter system-wide alert message"
            Layout.fillWidth: true
            wrapMode: TextEdit.Wrap
        }
        Button {
            text: "Send Alert"
            Layout.fillWidth: true
            onClicked: {
                Admin.sendAlert(alertText.text)
            }
        }

        // QR scanner
        Button {
            text: "Open QR Scanner"
            Layout.fillWidth: true
            onClicked: controller.loadPage("qrscanner.qml")
        }

        Button {
            text: "Back to Home"
            Layout.fillWidth: true
            onClicked: controller.loadPage("home.qml")
        }
    }

    Connections {
        target: Admin
        function onAlertSent(success, message) {
            console.log("Alert status:", message)
        }
    }
}

