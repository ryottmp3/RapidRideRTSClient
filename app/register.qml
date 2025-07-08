// register.qml — user registration with field guidance and popups
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: Theme.background
    anchors.fill: parent

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 16
        width: parent.width * 0.85

        Label {
            text: "Create Your Account"
            font.pixelSize: 24
            font.bold: true
            color: Theme.text
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }

        // Username
        Label {
            text: "Username"
            color: Theme.text
            font.pixelSize: 16
        }
        TextField {
            id: usernameField
            placeholderText: "e.g. transitfan99"
            font.pixelSize: 16
            Layout.fillWidth: true
        }

        // Email
        Label {
            text: "Email (optional)"
            color: Theme.text
            font.pixelSize: 16
        }
        TextField {
            id: emailField
            placeholderText: "e.g. user@example.com"
            font.pixelSize: 16
            Layout.fillWidth: true
        }

        // Password
        Label {
            text: "Password"
            color: Theme.text
            font.pixelSize: 16
        }
        TextField {
            id: passwordField
            placeholderText: "Create a secure password"
            echoMode: TextInput.Password
            font.pixelSize: 16
            Layout.fillWidth: true
        }

        // Register Button
        Button {
            text: "Register"
            Layout.fillWidth: true
            onClicked: {
                if (!usernameField.text || !passwordField.text) {
                    errorPopup.text = "Username and password are required."
                    errorPopup.open()
                } else {
                    AuthStore.register(
                        usernameField.text,
                        emailField.text,
                        passwordField.text,
                        null
                    )
                }
            }
        }

        // Switch to Login
        Button {
            text: "Already have an account? Log in"
            Layout.fillWidth: true
            onClicked: controller.loadPage("login.qml")
        }
    }

       // Success dialog
    Dialog {
        id: successDialog
        title: "Success"
        modal: true
        standardButtons: Dialog.Ok

        onAccepted: controller.loadPage("home.qml")

        contentItem: Text {
            text: "Account created. You are now logged in."
            wrapMode: Text.Wrap
            font.pixelSize: 16
        }
    }

    // Error popup
    Popup {
        id: errorPopup
        modal: true
        width: parent.width * 0.8
        height: 120
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        property alias text: errorText.text

        background: Rectangle {
            color: Theme.surface
            border.color: Theme.accent
            radius: 10
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Label {
                id: errorText
                color: Theme.text
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            Button {
                text: "OK"
                Layout.alignment: Qt.AlignRight
                onClicked: errorPopup.close()
            }
        }
    }

    // Backend error binding
    Connections {
        target: AuthStore
        onErrorOccurred: function(message) {
            errorPopup.text = message
            errorPopup.open()
        }
    }
}

