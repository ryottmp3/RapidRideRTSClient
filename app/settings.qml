// settings.qml – Settings page with theme selector and secure actions
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: settingsPage
    width: parent.width
    height: parent.height
    color: Theme.background

    property alias selectedTheme: themeSelector.currentText

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        Label {
            text: "Settings"
            font.pixelSize: 24
            font.bold: true
            color: Theme.text
        }

        // Theme selection
        ComboBox {
            id: themeSelector
            Layout.fillWidth: true
            model: ThemeList
            currentIndex: ThemeList.indexOf(Theme.currentTheme)
            onCurrentTextChanged: Theme.setTheme(currentText)
        }
        // Keep QML dropdown in sync if theme changed from outside
        Connections {
            target: Theme
            function onCurrentThemeChanged() {
                let idx = ThemeList.indexOf(Theme.currentTheme)
                if (idx >= 0 && themeSelector.currentIndex !== idx)
                    themeSelector.currentIndex = idx
            }
        }

        // Secure Card Storage Toggle
        CheckBox {
            id: cardStorageToggle
            text: "Enable Secure Card Storage"
            checked: true
            onCheckedChanged: {
                infoPopup.text = checked ?
                    "Card storage enabled securely." :
                    "Card storage disabled."
                infoPopup.open()
            }
        }

        // Logout Button
        Button {
            text: "Logout"
            Layout.fillWidth: true
            onClicked: {
                infoPopup.text = "You have been logged out."
                infoPopup.open()
                AuthStore.logout()
                controller.loadPage("login.qml")
            }
        }

        // Report Problem Button
        Button {
            text: "Report a Problem"
            Layout.fillWidth: true
            onClicked: {
                infoPopup.text = "To report issues, contact support@rapidride.app"
                infoPopup.open()
            }
        }

        // Back Home
        Button {
            text: "Back to Home"
            Layout.fillWidth: true
            onClicked: controller.loadPage("home.qml")
        }
    }

    // Reusable popup
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

