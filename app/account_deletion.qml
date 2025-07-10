// account_delete.qml – account deletion confirmation
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: deletePage
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: Theme.background

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20
            width: parent.width * 0.85

            Label {
                text: "Delete Account?"
                font.pixelSize: 26
                font.bold: true
                color: Theme.highlight
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
            }

            Text {
                text: "Are you sure you want to delete your account?\nThis action cannot be undone."
                font.pixelSize: 16
                color: Theme.text
                wrapMode: Text.Wrap
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
            }

            Button {
                text: "Yes, delete my account"
                Layout.fillWidth: true
                background: Rectangle {
                    color: "#c62828"  // red for destructive action
                    radius: 8
                    border.color: "#b71c1c"
                    border.width: 1
                }
                onClicked: {
                    AuthStore.delete_my_account()
                    infoPopup.text = "Your account has been deleted."
                    infoPopup.open()
                }
            }

            Button {
                text: "Cancel"
                Layout.fillWidth: true
                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 8
                    border.color: Theme.accent
                    border.width: 1
                }
                onClicked: controller.loadPage("account.qml")
            }
        }
    }

    Popup {
        id: infoPopup
        modal: true
        width: 300
        height: 140
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
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
                onClicked: {
                    infoPopup.close()
                    controller.loadPage("login.qml")
                }
            }
        }

        property string text: "Default Message"
    }
}

