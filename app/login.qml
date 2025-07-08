// login.qml — user login with labeled fields and popup feedback
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
            text: "Log In"
            font.pixelSize: 24
            font.bold: true
            color: Theme.text
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }

        // Username
        Label { text: "Username"; color: Theme.text; font.pixelSize: 16 }
        TextField {
            id: usernameField
            placeholderText: "Enter your username"
            font.pixelSize: 16
            Layout.fillWidth: true
        }

        // Password
        Label { text: "Password"; color: Theme.text; font.pixelSize: 16 }
        TextField {
            id: passwordField
            placeholderText: "Enter your password"
            echoMode: TextInput.Password
            font.pixelSize: 16
            Layout.fillWidth: true
        }

        // Login button
        Button {
            text: "Log In"
            Layout.fillWidth: true
            onClicked: {
                if (!usernameField.text || !passwordField.text) {
                    errorPopup.text = "Both fields are required."
                    errorPopup.open()
                } else {
                    AuthStore.login(usernameField.text, passwordField.text, null)
                }
            }
        }

        // Switch to Register
        Button {
            text: "Don't have an account? Register"
            Layout.fillWidth: true
            onClicked: controller.loadPage("register.qml")
        }
    }

    // Error Popup
    Popup {
        id: errorPopup
        modal: true
        width: parent.width * 0.8
        height: 120
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        property alias text: errorText.text

        background: Rectangle {
            color: Theme.background
            border.color: Theme.accent
            radius: 10
        }

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 16; spacing: 12

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

    // Backend Error Listener
    Connections {
        target: AuthStore
        function onErrorOccurred(message) {
            errorPopup.text = message
            errorPopup.open()
        }
    }

    // ** New: handle loginFinished to advance to home.qml **
    Connections {
        target: AuthStore
        function onLoginFinished(success, message) {
            if (success) {
                controller.loadPage("home.qml")
            } else {
                errorPopup.text = message
                errorPopup.open()
            }
        }
    }
}

