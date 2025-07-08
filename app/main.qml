import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: root
    visible: true
    width: 400
    height: 720
    title: qsTr("RTS RapidRide")
    property string currentPage: "login.qml"

    // Shared gradient background
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0f0f0f" }
            GradientStop { position: 1.0; color: "#1a1a1a" }
        }
    }

    // Persistent navigation drawer
    Drawer {
        id: navDrawer
        width: parent.width * 0.75
        height: parent.height
        edge: Qt.LeftEdge
        modal: true
        background: Rectangle { color: Theme.background }

        ColumnLayout {
            anchors.fill: parent
            spacing: 16

            // Profile section
            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: 12
                Rectangle {
                    width: 48; height: 48; radius: 24; color: "#444"
                    Image {
                        anchors.fill: parent
                        source: "assets/default_user_photo.png"
                        fillMode: Image.PreserveAspectCrop
                        smooth: true
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            navDrawer.close()
                            controller.loadPage("account.qml")
                        }
                    }
                }
            }

            Rectangle { height: 1; width: parent.width; color: Theme.border }

            // Navigation items
            ColumnLayout { spacing: 10
                Text {
                    text: "🏠 Home"; font.pixelSize: 16; color: Theme.accent
                    Layout.alignment: Qt.AlignLeft
                    MouseArea { anchors.fill: parent; onClicked: { navDrawer.close(); controller.loadPage("home.qml") } }
                }
                Text {
                    text: "🛒 Purchase Tickets"; font.pixelSize: 16; color: Theme.accent
                    Layout.alignment: Qt.AlignLeft
                    MouseArea { anchors.fill: parent; onClicked: { navDrawer.close(); controller.loadPage("purchasing.qml") } }
                }
                Text {
                    text: "🎟 Wallet"; font.pixelSize: 16; color: Theme.accent
                    Layout.alignment: Qt.AlignLeft
                    MouseArea { anchors.fill: parent; onClicked: { navDrawer.close(); controller.loadPage("wallet.qml") } }
                }
                Text {
                    text: "📍 Routes"; font.pixelSize: 16; color: Theme.accent
                    Layout.alignment: Qt.AlignLeft
                    MouseArea { anchors.fill: parent; onClicked: { navDrawer.close(); controller.loadPage("routes.qml") } }
                }
                Text {
                    text: "⚙ Settings"; font.pixelSize: 16; color: Theme.accent
                    Layout.alignment: Qt.AlignLeft
                    MouseArea { anchors.fill: parent; onClicked: { navDrawer.close(); controller.loadPage("settings.qml") } }
                }
                Text {
                    text: "🚪 Logout"; font.pixelSize: 16; color: Theme.accent
                    Layout.alignment: Qt.AlignLeft
                    MouseArea { anchors.fill: parent; onClicked: { navDrawer.close(); AuthStore.logout(); controller.loadPage("login.qml") } }
                }
            }
        }
    }

    // Top toolbar with hamburger and logo
    ToolBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 50
        background: Rectangle { color: Theme.accent }
        contentItem: RowLayout {
            anchors.fill: parent
            spacing: 8

            // Hamburger menu button
            ToolButton {
                id: menuButton
                text: "\u2261"
                font.pixelSize: 24
                visible: currentPage !== "login.qml" && currentPage !== "register.qml"
                Layout.preferredWidth: 40
                Layout.preferredHeight: 40
                Layout.alignment: Qt.AlignVCenter
                onClicked: navDrawer.open()
            }

            // Spacer pushes content left
            Item { Layout.fillWidth: true }

            // Logo image
            Image {
                id: logo
                source: "assets/rapidride.png"
                fillMode: Image.PreserveAspectFit
                Layout.preferredWidth: 200
                Layout.preferredHeight: 40
                Layout.alignment: Qt.AlignVCenter
            }

            // Spacer pushes content right
            Item { Layout.fillWidth: true }
        }
    }


    // Central loader to switch between screens
    Loader {
        id: pageLoader
        objectName: "pageLoader"
        anchors.top: topBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        source: currentPage
        onSourceChanged: currentPage = source
    }

    onClosing: Qt.quit()
}

