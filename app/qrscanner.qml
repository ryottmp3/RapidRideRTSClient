// qrscanner.qml – Qt 6.9-compatible camera QR scanner with overlay
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 6.6

Rectangle {
    id: root
    color: Theme.background
    anchors.fill: parent

    property int qrX: 0
    property int qrY: 0
    property int qrW: 0
    property int qrH: 0
    property bool showOverlay: false

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            text: "Scan a QR Code"
            font.pixelSize: 24
            color: Theme.text
            Layout.alignment: Qt.AlignHCenter
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 240

            VideoOutput {
                id: videoView
                anchors.fill: parent
                fillMode: VideoOutput.PreserveAspectCrop
            }

            Rectangle {
                x: qrX
                y: qrY
                width: qrW
                height: qrH
                visible: showOverlay
                color: "transparent"
                border.color: "#00FF00"
                border.width: 2
                radius: 4
            }

            Component.onCompleted: {
                console.log("videoView.videoSink is", videoView.videoSink)
                QrScanner.setVideoOutput(videoView)
            }
        }

        Button {
            text: "Back"
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                QrScanner.stop()
                controller.loadPage("home.qml")
            }
        }
    }

    Connections {
        target: QrScanner

        function onQrScanned(data) {
            console.log("Scanned:", data)
            showOverlay = true
            controller.loadPage("validate.qml")  // or handle payload
        }

        function onQrBoundingBox(x, y, w, h) {
            console.log("Bounding Box: ", x, y, w, h)
            qrX = x
            qrY = y
            qrW = w
            qrH = h
            showOverlay = true
        }

        function onErrorOccurred(msg) {
            console.error("Scanner error:", msg)
        }
    }
}

