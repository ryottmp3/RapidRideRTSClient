// validate.qml – Theme-integrated ticket validator
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: validationPage
    anchors.fill: parent
    color: Theme.background

    // Grab scanned ticket ID passed from controller
    property string scannedPayload: controller.pageData["scannedPayload"] || ""

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20
        width: parent.width * 0.8

        Label {
            text: "Ticket Validation"
            font.pixelSize: 24
            color: Theme.text
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }

        TextField {
            id: qrInput
            placeholderText: "Paste or scan ticket ID"
            text: scannedPayload
            onTextChanged: scannedPayload = text
            Layout.fillWidth: true
            color: Theme.text
            selectionColor: Theme.accent
            selectedTextColor: Theme.highlightedText
            background: Rectangle {
                color: Theme.buttonBackground
                radius: 4
            }
        }

        Button {
            text: "Validate Ticket"
            Layout.fillWidth: true
            enabled: scannedPayload.length > 0
            background: Rectangle {
                color: Theme.accent
                radius: 8
            }
            contentItem: Text {
                text: parent.text
                color: Theme.buttonText
                font.pixelSize: 16
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.centerIn: parent
            }
            onClicked: {
                resultLabel.text = "⏳ Validating..."
                Network.validateTicket(scannedPayload)
            }
        }

        Label {
            id: resultLabel
            text: ""
            color: Theme.text
            font.pixelSize: 16
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        Button {
            text: "Back"
            Layout.alignment: Qt.AlignHCenter
            background: Rectangle {
                color: Theme.buttonBackground
                radius: 8
            }
            contentItem: Text {
                text: parent.text
                color: Theme.buttonText
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.centerIn: parent
            }
            onClicked: controller.loadPage("admin.qml")
        }
    }

    Connections {
        target: Network

        function onTicketValidated(response) {
            if (response.status === "valid") {
                resultLabel.text = "✅ Ticket valid!"
            } else if (response.status === "already_used") {
                resultLabel.text = "⚠️ Ticket has already been used."
            } else if (response.status === "invalid") {
                resultLabel.text = "❌ Invalid ticket."
            } else {
                resultLabel.text = "❓ Unknown error occurred."
            }
        }
    }

    Component.onCompleted: {
        if (scannedPayload.length > 0) {
            resultLabel.text = "⏳ Validating..."
            Network.validateTicket(scannedPayload)
        }
    }
}

