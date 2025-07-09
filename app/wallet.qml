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

            delegate: Rectangle {
                width: parent.width
                height: 80
                radius: 8
                color: Theme.toolTipBase
                border.color: Theme.accent
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    ColumnLayout {
                        spacing: 2
                        Label {
                            text: "RapidRide Ticket Type: " + formatTicketType(modelData.ticket_type) 
                            color: Theme.text
                            font.pixelSize: 14
                        }
                        Label {
                            text: "Ticket Valid for: " + formatValidFor(modelData.valid_for)
                            color: Theme.text
                            font.pixelSize: 12
                        }
                        Label {
                            text: "Issued: " + modelData.issued_at
                            color: Theme.text
                            font.pixelSize: 12
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Button {
                        text: "QR"
                        onClicked: {
                            console.log("\n\nmodel: ", model)
                            var currentTicketId = modelData.ticket_id
                            QrGen.makeQr(modelData.ticket_id)
                            qrPopup.open()
                        }
                    }
                }
            }
        }
    }

    function formatTicketType(raw) {
        switch (raw) {
            case "single_use": return "<b>Single Ride</b>"
            case "monthly_pass": return "<b>Monthly Pass</b>"
            default: return raw
        }
    }

    function formatValidFor(raw) {
        switch (raw) {
            case "None": return "Any Time"
            default: return raw
        }
    }
 
        // QR Popup
    Popup {
        id: qrPopup
        modal: true
        width: parent.width      // full window width
        height: parent.height * 0.6
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            color: Theme.background
            border.color: Theme.border
            radius: 10
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Label {
                text: qsTr("Your Ticket")
                font.pixelSize: 20
                color: Theme.text
                Layout.alignment: Qt.AlignHCenter
            }

            Image {
                id: qrCodeImage
                fillMode: Image.PreserveAspectFit
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            Button {
                id: closeButton
                text: qsTr("Close")
                Layout.alignment: Qt.AlignHCenter
                background: Rectangle {
                    radius: 6
                    color: Theme.accent
                }
                contentItem: Text {
                    text: closeButton.text
                    anchors.centerIn: parent
                    color: Theme.text
                }
                onClicked: qrPopup.close()
            }
        }
    }

    // Listen for Network signals
    Connections {
        target: Network
        function onTicketGenerated(payload) {
            QrGen.makeQr(payload)
        }
        function onErrorOccurred(err) {
            text = qsTr("Error: ") + err
        }
    }

    // Listen for QR generation
    Connections {
        target: QrGen
        function onQrGenerated(dataUri) {
            qrCodeImage.source = dataUri
            qrPopup.open()
        }
    }
}

