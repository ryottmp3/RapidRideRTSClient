// account_settings.qml – editable account management UI
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
            spacing: 10

            Label {
                text: "Edit Account Settings"
                font.pixelSize: 24
                font.bold: true
                color: Theme.text
            }

            ColumnLayout {
                spacing: 10

                Label { text: "Display Name"; color: Theme.text }
                TextField {
                    id: displayNameField
                    placeholderText: AuthStore.displayName()
                    color: Theme.text
                    Layout.fillWidth: true
                }

                Label { text: "Username"; color: Theme.text }
                TextField {
                    id: usernameField
                    placeholderText: AuthStore.username()
                    color: Theme.text
                    Layout.fillWidth: true
                }

                Label { text: "Email"; color: Theme.text }
                TextField {
                    id: emailField
                    placeholderText: AuthStore.email()
                    color: Theme.text
                    Layout.fillWidth: true
                }

                Label { text: "New Password"; color: Theme.text }
                TextField {
                    id: newPasswordField
                    placeholderText: "Enter new password"
                    echoMode: TextInput.Password
                    color: Theme.text
                    Layout.fillWidth: true
                }

                Label { text: "Confirm Password"; color: Theme.text }
                TextField {
                    id: confirmPasswordField
                    placeholderText: "Re-enter new password"
                    echoMode: TextInput.Password
                    color: Theme.text
                    Layout.fillWidth: true
                }
            }

            Button {
                text: "Save Changes"
                Layout.fillWidth: true
                Layout.preferredHeight: 64
                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 8
                    border.color: Theme.accent
                    border.width: 1
                }
                onClicked: {
                    if (newPasswordField.text !== confirmPasswordField.text) {
                        infoPopup.text = "Passwords do not match."
                        infoPopup.open()
                        return
                    }

                    AuthStore.update_account_settings(
                        displayNameField.text,
                        usernameField.text,
                        emailField.text,
                        newPasswordField.text
                    )
                }
            }
            
            Button {
                text: "Delete Account"
                Layout.fillWidth: true
                background: Rectangle {
                    color: "#7c0a02"
                    radius: 8
                    border.color: Theme.accent
                    border.width: 1
                }
                onClicked: controller.loadPage("account_deletion.qml")
            }

            Button {
                text: "Back to Home"
                Layout.fillWidth: true
                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 8
                    border.color: Theme.accent
                    border.width: 1
                }
                onClicked: controller.loadPage("home.qml")
            }
        }
    }

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

