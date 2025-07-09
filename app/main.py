# main.py
# Main entry point for the RapidRide QML application
import os
import io
import base64
import segno
import sys
import argparse
import logging
from network import NetworkManager
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QUrl, Signal, Property, QCoreApplication
from PySide6.QtGui import QDesktopServices, QGuiApplication, QPalette, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from theme_manager import ThemeManager
from wallet_store import WalletStore
from auth_store import AuthStore
from admin import AdminStore
from qr_scanner import QrScanner


class Browser(QWidget):
    checkoutSuccess = Signal()
    checkoutFailure = Signal()

    def __init__(self):
        super(Browser, self).__init__()
        self.logger = logging.getLogger("rt.client.main")
        self.setWindowTitle("Stripe Checkout")
        self.resize(400, 720)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.webV = QWebEngineView(self)
        layout.addWidget(self.webV)
        self.webV.urlChanged.connect(self._on_url_changed)

    @Slot(str)
    def loadUrl(self, url:str):
        """Loads a URL into WebEngine"""
        self.webV.load(QUrl(url))

    @Slot(QUrl)
    def _on_url_changed(self, qurl: QUrl):
        url = qurl.toString()
        self.logger.debug(f"Redirect URL: {url}")
        if "payment-success" in url:
            # Close the widget
            self.logger.debug(f"Payment Successful!")
            self.checkoutSuccess.emit()
            self.close()
        elif "8000" not in url:
            pass
        else:
            self.logger.debug(f"Payment Unsuccessful, Someone's Broke!")
            self.checkoutFailure.emit()
            self.close()
            self.logger.debug(f"Browser Widget Closed.")


class CLIConfig:
    """
    Parses command-line arguments and configures logging.
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="RapidRide QML Client")
        self.parser.add_argument(
            "--log-level", "-l",
            default=os.getenv("LOG_LEVEL", "DEBUG"),
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the logging level"
        )
        self.args = self.parser.parse_args()
        self.configure_logging()

    def configure_logging(self):
        level = getattr(logging, self.args.log_level, logging.DEBUG)
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
        self.logger = logging.getLogger("rts.client.main")
        self.logger.debug("Starting QML client with log level=%s", self.args.log_level)


class PdfViewer(QMainWindow):
    def __init__(self, pdf_path):
        super().__init__()
        logger = logging.getLogger("rts.client.main")
        logger.debug(f"Initializing PdfViewer for {pdf_path}")
        self.setWindowTitle("PDF Viewer")

        self.pdf_document = QPdfDocument(self)
        self.pdf_document.load(pdf_path)

        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.pdf_document)

        self.setCentralWidget(self.pdf_view)
        self.resize(800, 600)

class ThemeController(QObject):
    themeChanged = Signal()

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("rts.client.main")
        self.logger.debug("ThemeController init")
        self._theme_manager = ThemeManager()
        self._current_theme = self._theme_manager.get_theme()
        self._theme_data = self._theme_manager.get_theme_data()

    @Slot(str)
    def setTheme(self, name):
        self.logger.debug("Setting theme to %s", name)
        self._theme_manager.set_theme(name)
        self._current_theme = name
        self._theme_data = self._theme_manager.get_theme_data()
        self.applyPalette(name)
        self.themeChanged.emit()

    @Property(str, notify=themeChanged)
    def available_themes(self):
        return self._theme_manager.available_themes()

    @Property(str, notify=themeChanged)
    def currentTheme(self):
        return self._current_theme

    @Property(str, notify=themeChanged)
    def background(self):
        return self._theme_data.get("background", "#000000")

    @Property(str, notify=themeChanged)
    def text(self):
        return self._theme_data.get("text", "#ffffff")

    @Property(str, notify=themeChanged)
    def accent(self):
        return self._theme_data.get("accent", "#f5721b")

    @Property(str, notify=themeChanged)
    def border(self):
        return self._theme_data.get("border", "#f5721b")

    @Property(str, notify=themeChanged)
    def buttonBackground(self):
        return self._theme_data.get("buttonBackground", "#1e1e1e")

    @Property(str, notify=themeChanged)
    def buttonText(self):
        return self._theme_data.get("buttonText", "#ffffff")

    @Property(str, notify=themeChanged)
    def toolTipBase(self):
        return self._theme_data.get("toolTipBase", "#2c2c2c")

    @Property(str, notify=themeChanged)
    def toolTipText(self):
        return self._theme_data.get("toolTipText", "#ffffff")

    @Property(str, notify=themeChanged)
    def highlight(self):
        return self._theme_data.get("highlight", "#f5721b")

    @Property(str, notify=themeChanged)
    def highlightedText(self):
        return self._theme_data.get("highlightedText", "#000000")

    @Property(str, notify=themeChanged)
    def placeholder(self):
        return self._theme_data.get("placeholder", "#888888")

    @Property(str, notify=themeChanged)
    def link(self):
        return self._theme_data.get("link", "#268bd2")

    def applyPalette(self, theme):
        self.logger.debug(f"Applying palette for theme {theme}")
        palette = QPalette()
        colors = self._theme_data

        palette.setColor(QPalette.Window, QColor(colors.get("background", "#000000")))
        palette.setColor(QPalette.WindowText, QColor(colors.get("text", "#ffffff")))
        palette.setColor(QPalette.Base, QColor(colors.get("background", "#000000")))
        palette.setColor(QPalette.AlternateBase, QColor(colors.get("background", "#000000")))
        palette.setColor(QPalette.ToolTipBase, QColor(colors.get("toolTipBase", "#2c2c2c")))
        palette.setColor(QPalette.ToolTipText, QColor(colors.get("toolTipText", "#ffffff")))
        palette.setColor(QPalette.Text, QColor(colors.get("text", "#ffffff")))
        palette.setColor(QPalette.Button, QColor(colors.get("buttonBackground", "#1e1e1e")))
        palette.setColor(QPalette.ButtonText, QColor(colors.get("buttonText", "#ffffff")))
        palette.setColor(QPalette.BrightText, QColor("#ff0000"))
        palette.setColor(QPalette.Highlight, QColor(colors.get("highlight", "#f5721b")))
        palette.setColor(QPalette.HighlightedText, QColor(colors.get("highlightedText", "#000000")))
        palette.setColor(QPalette.PlaceholderText, QColor(colors.get("placeholder", "#888888")))
        palette.setColor(QPalette.Link, QColor(colors.get("link", "#268bd2")))

        QGuiApplication.setPalette(palette)


class Controller(QObject):
    def __init__(self, loader):
        super().__init__()
        self.loader = loader
        self._pendingPageData = {}
        self.logger = logging.getLogger("rts.client.main")

    @Slot(str)
    def loadPage(self, page):
        self.logger.debug("Loading page: %s", page)
        self._pendingPageData = {}  # clear if no data
        self.loader.setProperty("source", page)

    @Slot(str, 'QVariantMap')
    def loadPageWithData(self, page, data):
        self.logger.debug(f"Loading page: {page} with data: {data}")
        self._pendingPageData = data
        self.loader.setProperty("source", page)

    @Property('QVariantMap')
    def pageData(self):
        return self._pendingPageData

# class Controller(QObject):
#     """Handles Navigation between QML pages using a Loader"""
#     def __init__(self, loader):
#         super().__init__()
#         self.loader = loader
#         self.logger = logging.getLogger("rts.client.main")
# 
#     @Slot(str)
#     def loadPage(self, page):
#         self.logger.debug("Loading page: %s", page)
#         self.loader.setProperty("source", page)

class AppBackend(QObject):
    checkoutSuccess = Signal()
    checkoutFailure = Signal()
    """Exposes Python-side functionality like viewing PDFs, ticket management"""

    def __init__(self, browser: Browser):
        super().__init__()
        self.browser = browser
        self._windows = []
        self.logger = logging.getLogger("rts.client.main")
        self.browser.checkoutSuccess.connect(self.checkoutSuccess)
        self.browser.checkoutFailure.connect(self.checkoutFailure)

    @Slot(str)
    def open_pdf_viewer(self, fname):
        """Opens the requested PDF in an external viewer"""
        self.logger.debug("open_pdf_viewer called with %s", fname)
        pdf_path = f"assets/routes/{fname}-map2025.pdf"
        viewer = PdfViewer(pdf_path)
        viewer.show()
        self._windows.append(viewer)

    @Slot(str)
    def purchase_ticket(self, session_url: str):
        self.logger.debug(f"Opening Stripe Checkout: {session_url}")
        self.browser.loadUrl(session_url)
        self.browser.show()


class QrGenerator(QObject):
    """Generates QR Codes"""
    qrGenerated = Signal(str)  # Emits a full data-URI

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("rts.client.main")

    @Slot(str)
    def makeQr(
        self,
        payload: str
    ):
        """Makes a QR Code"""
        # Create QR Code
        self.logger.debug("Initializing QR Code Generation")
        self.logger.debug("Creating QR Code")
        qr = segno.make(payload, error='m')

        # Write in into an in-RAM PNG
        self.logger.debug("Writing QR Code to RAM")
        buf = io.BytesIO()
        qr.save(buf, kind='png', scale=4)
        img_bytes = buf.getvalue()

        # Base64-encode and wrap as data URI
        self.logger.debug("Encoding QR Code as Base64 URI")
        b64 = base64.b64encode(img_bytes).decode('ascii')
        data_uri = f"data:image/png;base64,{b64}"

        # Send back to QML
        self.logger.debug("Emitting Data URI Back to QML")
        self.qrGenerated.emit(data_uri)


if __name__ == "__main__":
    config = CLIConfig()
    logger = config.logger
    logger.debug("Application startup begin")

    QCoreApplication.setOrganizationName("RapidRide")
    QCoreApplication.setApplicationName("RTS Client")
    app = QApplication(sys.argv)

    logger.debug("Initializing QQmlApplicationEngine")
    engine = QQmlApplicationEngine()
    theme_controller = ThemeController()
    qrgen = QrGenerator()
    wallet_store = WalletStore()
    auth_store = AuthStore(api_url = os.getenv("API_URL", "http://127.0.0.1:8000"))
    admin_store = AdminStore(auth_store)
    qr_scanner = QrScanner()
    browser = Browser()
    theme_controller.applyPalette(theme_controller.currentTheme)
    engine.rootContext().setContextProperty("ThemeController", theme_controller)
    engine.rootContext().setContextProperty("ThemeManager", theme_controller)
    engine.rootContext().setContextProperty("Theme", theme_controller)
    engine.rootContext().setContextProperty("ThemeList", theme_controller.available_themes)
    engine.rootContext().setContextProperty("QrGen", qrgen)
    engine.rootContext().setContextProperty("WalletStore", wallet_store)
    engine.rootContext().setContextProperty("AuthStore", auth_store)
    engine.rootContext().setContextProperty("Admin", admin_store)
    engine.rootContext().setContextProperty("QrScanner", qr_scanner)
    engine.rootContext().setContextProperty("Browser", browser)

    logger.debug("Loading QML file: main.qml")
    engine.load("main.qml")
    if not engine.rootObjects():
        logger.error("Failed to load main.qml, exiting")
        sys.exit(-1)

    root = engine.rootObjects()[0]
    loader = root.findChild(QObject, "pageLoader")
    if loader is None:
        logger.error("Loader 'pageLoader' not found, exiting")
        sys.exit(-1)

    logger.debug("Setting up NetworkManager, Controller, AppBackend")
    network = NetworkManager(os.getenv("API_URL", "http://127.0.0.1:8000"), auth_store=auth_store)
    backend = AppBackend(browser)
    controller = Controller(loader)
    engine.rootContext().setContextProperty("Network", network)
    engine.rootContext().setContextProperty("controller", controller)
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("Theme", theme_controller)
    engine.rootContext().setContextProperty("PageLoader", loader)

    initial_page = "home.qml" if network.isLoggedIn() else "login.qml"
    logger.debug("Setting initial page: %s", initial_page)
    engine.rootContext().setContextProperty("Theme", theme_controller)
    loader.setProperty("source", initial_page)

    logger.debug("Starting Qt event loop")
    sys.exit(app.exec())

