// account_settings.qml – dedicated account management UI
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: accountPage
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: Theme.background

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 20

            Label {
                text: "Account Settings"
                font.pixelSize: 24
                font.bold: true
                color: Theme.text
            }

            // Display name (placeholder only)
            TextField {
                id: displayNameField
                placeholderText: "Display Name"
                text: ""
                Layout.fillWidth: true
                font.pixelSize: 16
                color: Theme.text
                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 6
                    border.color: Theme.border
                }
            }

            // Email (disabled for now)
            TextField {
                id: emailField
                placeholderText: "Email (read-only)"
                text: "user@example.com"
                enabled: false
                Layout.fillWidth: true
                font.pixelSize: 16
                color: Theme.text
                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 6
                    border.color: Theme.border
                }
            }

            // Change Password button
            Button {
                text: "Change Password"
                Layout.fillWidth: true
                onClicked: {
                    infoPopup.text = "Password reset functionality is not implemented yet."
                    infoPopup.open()
                }
            }

            // Delete Account button
            Button {
                text: "Delete Account"
                Layout.fillWidth: true
                background: Rectangle {
                    color: "#aa0000"
                    radius: 6
                }
                onClicked: {
                    infoPopup.text = "Account deletion not yet supported."
                    infoPopup.open()
                }
            }

            // Back to Home
            Button {
                text: "Back to Home"
                Layout.fillWidth: true
                onClicked: controller.loadPage("home.qml")
            }
        }
    }

    // Info popup
    Popup {
        id: infoPopup
        modal: true
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 300
        height: 140
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            color: Theme.background
            border.color: Theme.accent
            radius: 10
        }

        Column {
            anchors.centerIn: parent
            spacing: 12

            Text {
                id: popupText
                text: infoPopup.text
                color: Theme.text
                font.pixelSize: 16
                wrapMode: Text.Wrap
                horizontalAlignment: Text.AlignHCenter
            }

            Button {
                text: "OK"
                width: 80
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: infoPopup.close()
            }
        }

        property string text: "Default Message"
    }
}

