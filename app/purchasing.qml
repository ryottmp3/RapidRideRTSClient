// purchasing.qml – modern ticket purchasing page with QR & theming
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: mall
    anchors.fill: parent

    // ===== User Selection ===================================================
    property string selectedTicketType: ""
    property string selectedMonth: ""
    property string selectedYear: ""
    // ========================================================================

    // Background uses Theme
    Rectangle {
        anchors.fill: parent
        color: Theme.background
    }

    ColumnLayout {
        id: content
        anchors.fill: parent
        anchors.margins: 24
        spacing: 20

        Label {
            text: qsTr("Purchase Ticket")
            font.pixelSize: 24
            color: Theme.text
            Layout.alignment: Qt.AlignHCenter
        }

        ComboBox {
            id: ticketTypeCombo
            Layout.fillWidth: true
            model: [
                { text: qsTr("Single Use"), value: "single_use" },
                { text: qsTr("10 Pack"), value: "ten_pack" },
                { text: qsTr("Monthly Pass"), value: "monthly_pass" }
            ]
            textRole: "text"
            valueRole: "value"
            onActivated: {
                index => description.text = model[index].text + " " + qsTr("selected")
            }
        }

            // These only show up when Monthly Pass is chosen
        RowLayout {
            id: monthYearRow
            Layout.fillWidth: true
            spacing: 8
            visible: ticketTypeCombo.currentValue === "monthly_pass"

            ComboBox {
                id: monthCombo
                Layout.preferredWidth: 120
                currentIndex: -1
                displayText: currentIndex === -1 ? "Choose Month..." : currentText
                model: [
                    qsTr("January"), qsTr("February"), qsTr("March"),
                    qsTr("April"),   qsTr("May"),      qsTr("June"),
                    qsTr("July"),    qsTr("August"),   qsTr("September"),
                    qsTr("October"), qsTr("November"), qsTr("December")
                ]
            }

            ComboBox {
                id: yearCombo
                Layout.preferredWidth: 100
                currentIndex: -1
                displayText: currentIndex === -1 ? "Choose Year..." : currentText
                model: [2025, 2026, 2027, 2028, 2029, 2030]
                textRole: ""  // the numbers will show as-is
            }
        }

        TextArea {
            id: description
            readOnly: true
            text: qsTr("Choose a ticket type above.")
            wrapMode: Text.WordWrap
            color: Theme.text
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            background: Rectangle { color: Theme.background }
        }

        Button {
            id: buyButton
            Layout.fillWidth: true
            height: 56
            text: qsTr("Buy Now")
            font.pixelSize: 18
            background: Rectangle {
                radius: 8
                color: Theme.accent
            }
            contentItem: Text {
                text: buyButton.text
                anchors.centerIn: parent
                color: Theme.text
                font.pixelSize: 18
                font.bold: true
            }
            
            // disable if monthly_pass but no month or year chosen
            enabled: !(ticketTypeCombo.currentValue === "monthly_pass"
            && (monthCombo.currentIndex < 0 || yearCombo.currentIndex < 0))

            onClicked: {
                busy.visible = true
                mall.selectedTicketType = ticketTypeCombo.currentValue
                if (ticketTypeCombo.currentValue === "monthly_pass") {
                    console.log("Buying pass for", monthCombo.currentText, yearCombo.currentText)
                    mall.selectedMonth == monthCombo.currentText
                    mall.selectedYear = yearCombo.currentText
                }
                Network.createCheckoutSession(
                    ticketTypeCombo.model[ticketTypeCombo.currentIndex].value,
                    null
                )
            }
        }

        BusyIndicator {
            id: busy
            width: 32; height: 32
            running: visible
            visible: false
            Layout.alignment: Qt.AlignHCenter
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
                id: qrImage
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
            busy.visible = false
            QrGen.makeQr(payload)
        }
        function onErrorOccurred(err) {
            busy.visible = false
            description.text = qsTr("Error: ") + err
        }
    }

    // Listen for QR generation
    Connections {
        target: QrGen
        function onQrGenerated(dataUri) {
            qrImage.source = dataUri
            qrPopup.open()
        }
    }

    // Listen for Stripe Checkout URL
    Connections {
        target: Network
        function onCheckoutSessionCreated(sessionUrl) {
            busy.visible = false

            // Swop in the checkout page
            backend.purchase_ticket(sessionUrl)
        }
    }

    // Listen for Checkout Payment Success
    Connections {
        target: backend
        
        // Fired when Browser sees "payment-success" in url
        function onCheckoutSuccess() {
            Network.generateTicket(mall.selectedTicketType)
            controller.loadPage("wallet.qml")
        }

        // Fired when Browser doesn't see "payment-success" in url
        function onCheckoutFailure() {
            controller.loadPage("purchasing.qml")
        }
    }
}

