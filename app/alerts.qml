// alerts.qml – displays live alerts in card format
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    anchors.fill: parent
    color: Theme.background

    property var alertList: []

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            text: "Live Alerts"
            font.pixelSize: 24
            font.bold: true
            color: Theme.text
            Layout.alignment: Qt.AlignHCenter
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                id: alertContainer
                spacing: 12
                width: parent.width

                Repeater {
                    model: root.alertList

                    Rectangle {
                        width: parent.width
                        radius: 8
                        color: Theme.buttonBackground
                        border.color: Theme.accent
                        border.width: 1
                        padding: 12

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 6

                            Label {
                                text: modelData.message
                                color: Theme.text
                                wrapMode: Text.Wrap
                                font.pixelSize: 16
                            }

                            Label {
                                text: "Posted by " + modelData.issued_by + " at " + Qt.formatDateTime(new Date(modelData.issued_at), "MMM dd, hh:mm ap")
                                font.pixelSize: 12
                                color: Theme.placeholder
                            }
                        }
                    }
                }
            }
        }

        Button {
            text: "Refresh"
            Layout.alignment: Qt.AlignHCenter
            onClicked: loadAlerts()
        }
    }

    function loadAlerts() {
        fetch("http://127.0.0.1:8000/alerts")
            .then(response => response.json())
            .then(data => {
                root.alertList = data
            })
            .catch(err => {
                console.log("Failed to fetch alerts:", err)
            })
    }

    Component.onCompleted: loadAlerts()
}

