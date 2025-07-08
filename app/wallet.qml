// wallet.qml — Modern ticket wallet with QR viewer
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    anchors.fill: parent
    color: Theme.background
    Component.onCompleted: Network.fetchTickets()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            text: "My Tickets"
            font.pixelSize: 24
            color: Theme.text
        }

        // Empty state
        Label {
            id: emptyHint
            visible: Network.ticketList.length === 0
            text: "No tickets found. Purchase one to get started."
            color: Theme.text
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        // Ticket list
        ListView {
            id: ticketView
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            clip: true
            model: Network.ticketList
            //console.log(model)

            delegate: Rectangle {
                width: parent.width
                height: 80
                radius: 8
                color: Theme.card
                border.color: Theme.accent
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    ColumnLayout {
                        spacing: 2
                        Label {
                            text: model.ticket_type 
                            color: Theme.text
                            font.pixelSize: 14
                        }
                        Label {
                            text: "ID: " + model.ticket_id
                            color: Theme.text
                            font.pixelSize: 12
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Button {
                        text: "QR"
                        onClicked: {
                            busy.visible = true
                            console.log(model)
                            var currentTicketId = model.ticket_id
                            QrGen.makeQr(model.ticket_id)
                            qrPopup.open()
                        }
                    }
                }
            }
        }
    }

    // Popup for QR display
    Popup {
        id: qrPopup
        width: parent.width * 0.8
        height: parent.height * 0.6
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle {
            color: Theme.surface
            border.color: Theme.accent
            radius: 10
        }

        property string currentTicketId: ""
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 16

            BusyIndicator {
                id: busy
                visible: true
                running: visible
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Image {
                id: qrImage
                source: Network.qrImage
                fillMode: Image.PreserveAspectFit
                anchors.fill: parent
                visible: !busy.visible
            }

            Button {
                text: "Close"
                Layout.alignment: Qt.AlignHCenter
                onClicked: qrPopup.close()
            }
        }

        // Populate Wallet
        Connections {
            target: Network
            function onTicketsFetched(ticketList) {
                console.log("Got", ticketList.length, "tickets from Python")
                WalletStore.addMultipleTickets(ticketList)
            } 
        }
    }
}

