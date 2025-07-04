import QtQuick 2.15
import QtQuick.Controls 2.15
import QtWebView

Item {
    id: root
    property string sessionUrl: ""  // filled from loader

    WebView {
        id: webview
        anchors.fill: parent
        url: root.sessionUrl

        onUrlChanged: {
            var u = webview.url.toString()
            if (u.indexOf("/payment-success") !== -1) {
                // payment complete, pull down tickets
                Network.fetchTickets()
                controller.loadPage("wallet.qml") 
            }
        }
    }
}

