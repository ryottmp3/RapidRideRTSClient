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
            spacing: 10

            Label {
                text: "Account Settings"
                font.pixelSize: 24
                font.bold: true
                color: Theme.text
            }

            ColumnLayout {
                spacing: 5
                
                Label {
                    text: "Current Settings"
                    font.pixelSize: 18
                    font.bold: true
                    color: Theme.highlight
                }

                Text {
                    text: "<b>Display Name:</b> " + AuthStore.displayName()
                    font.pixelSize: 14
                    color: Theme.text
                }

                Text {
                    text: "<b>Username:</b> " + AuthStore.username()
                    font.pixelSize: 14
                    color: Theme.text
                }

                Text {
                    text: "<b>Email Address:</b> " + AuthStore.email()
                    font.pixelSize: 14
                    color: Theme.text
                }
            }

            Button {
                text: "Change Account Settings"
                Layout.fillWidth: true
                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 8
                    border.color: Theme.accent
                    border.width: 1
                }
                onClicked: {
                    controller.loadPage("account_modification.qml")
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

