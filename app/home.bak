// home.qml – content‑only page (App shell handles navigation)
// Themed version using ThemeController context properties

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    anchors.fill: parent
    color: Theme.background

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Big menu buttons using theme
        Repeater {
            model: [
                { label: "View Routes",       page: "routes.qml"     },
                { label: "Purchase Tickets",  page: "purchasing.qml" },
                { label: "Open Wallet",       page: "wallet.qml"     },
                { label: "View Alerts",       page: "alerts.qml"     },
                { label: "Settings",          page: "settings.qml"   }
            ]

            delegate: Button {
                Layout.fillWidth: true
                height: 60
                text: modelData.label
                font.pixelSize: 18

                background: Rectangle {
                    color: Theme.buttonBackground
                    radius: 8
                    border.color: Theme.accent
                    border.width: 1
                }

                contentItem: Text {
                    text: modelData.label
                    color: Theme.text
                    font.pixelSize: 18
                    anchors.centerIn: parent
                }

                onClicked: controller.loadPage(modelData.page)
            }
        }
    }
}

