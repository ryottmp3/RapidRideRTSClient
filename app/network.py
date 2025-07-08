# Network.py
#!/usr/bin/env python3
"""
network.py

QObject-based bridge between QML and the FastAPI backend.
All HTTP is done here; QML receives results via signals or optional callbacks.
Includes detailed debug logging and persistent auth token via QSettings.
"""
import base64
import logging
import requests
from PySide6.QtCore import QObject, Signal, Slot, QSettings, Property
from PySide6.QtQml import QJSValue

# Configure logger for this module
logger = logging.getLogger("rts.network")

class NetworkManager(QObject):
    # ----- Signals ---------------------------------------------------------
    loginFinished    = Signal(bool, str)   # success, message
    registerFinished = Signal(bool, str)   # success, message
    ticketGenerated  = Signal(str)         # base64 payload
    ticketsFetched   = Signal('QVariantList')        # list of dicts
    errorOccurred    = Signal(str)         # generic error
    checkoutSessionCreated = Signal(str)   # emits URL user must visit

    # ----- Init ------------------------------------------------------------
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        super().__init__()
        self.settings = QSettings()
        self.base_url = base_url
        self._auth_header: str | None = None
        self._ticket_list: list[dict] = []
        self._qr_image: str = ""
        # Load saved auth header, if any
        saved = self.settings.value("auth_header", "")
        if saved:
            self._auth_header = saved
            logger.debug("Loaded auth_header from QSettings: %s...", saved[:10])
        logger.debug("NetworkManager initialized with base_url=%s", self.base_url)

    # ----- Already Logged In? ---------------------------------------------
    @Slot(result=bool)
    def isLoggedIn(self) -> bool:
        logged_in = self._auth_header is not None
        logger.debug("isLoggedIn called, result=%s", logged_in)
        return logged_in

    # ----- Auth token helpers ---------------------------------------------
    def _set_token(self, token: str, token_type: str = "Bearer"):
        self._auth_header = f"{token_type} {token}"
        self.settings.setValue("auth_header", self._auth_header)
        logger.debug("Saved auth_header to QSettings: %s...", token[:10])

    # ----- Exposed properties (for wallet.qml) ----------------------------
    def _get_ticket_list(self):
        logger.debug("Retrieving ticket list, count=%d", len(self._ticket_list))
        return self._ticket_list

    ticketList = Property("QVariant", _get_ticket_list, constant=True)

    # ----- Login -----------------------------------------------------------
    @Slot(str, str, QJSValue, result=None)
    def login(self, username: str, password: str, callback: QJSValue | None = None):
        """OAuth2 password grant -> /token"""
        url = f"{self.base_url}/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"username": username, "password": password}
        logger.debug("Login request to %s with username=%s", url, username)
        try:
            r = requests.post(url, data=data, headers=headers, timeout=8)
            logger.debug("Login response status=%d", r.status_code)
            r.raise_for_status()
            resp_json = r.json()
            logger.debug("Login response JSON: %s", resp_json)
            self._set_token(resp_json["access_token"], resp_json["token_type"])
            msg = "Login successful."
            self.loginFinished.emit(True, msg)
            if callback and callback.isCallable():
                callback.call([True, msg])
        except Exception as e:
            logger.exception("Login failed for user %s", username)
            msg = f"Login failed: {e}"
            self.loginFinished.emit(False, msg)
            if callback and callback.isCallable():
                callback.call([False, msg])

    # ----- Registration ----------------------------------------------------
    @Slot(str, str, str, QJSValue, result=None)
    def register(self, username: str, email: str, password: str, callback: QJSValue | None = None):
        """Create account -> /register"""
        url = f"{self.base_url}/register"
        payload = {"username": username, "email": email or None, "password": password}
        logger.debug("Register request to %s payload=%s", url, payload)
        try:
            r = requests.post(url, json=payload, timeout=8)
            logger.debug("Register response status=%d", r.status_code)
            r.raise_for_status()
            resp_json = r.json()
            logger.debug("Register response JSON: %s", resp_json)
            # Store token from registration as well
            self._set_token(resp_json["access_token"], resp_json["token_type"])
            # auto-login for QML flow
            self.login(username, password)
            msg = "Registration successful."
            self.registerFinished.emit(True, msg)
            if callback and callback.isCallable():
                callback.call([True, msg])
        except Exception as e:
            logger.exception("Registration failed for user %s", username)
            msg = f"Registration failed: {e}"
            self.registerFinished.emit(False, msg)
            if callback and callback.isCallable():
                callback.call([False, msg])

    # ----- Logout ----------------------------------------------------------
    @Slot(result=None)
    def logout(self):
        """Clear JWT from memory (client-side logout)"""
        logger.debug("Logout called, clearing auth header and settings")
        self.settings.remove("auth_header")
        self._auth_header = None
        self._ticket_list = []
        self._qr_image = ""

    # ----- Create Stripe Checkout Session ---------------------------------
    @Slot(str, "QJSValue", result=None)
    def createCheckoutSession(
        self,
        ticket_type: str,
        callback: QJSValue = None
    ):
        """Ask server to create a Stripe checkout Session"""
        url = f"{self.base_url}/create-checkout-session"
        headers = {"Authorization": self._auth_header} if self._auth_header else {}
        try:
            logger.debug("Creating Stripe Checkout Session")
            r = requests.post(
                url,
                json={
                    "ticket_type": ticket_type
                },
                headers=headers,
                timeout=8
            )
            r.raise_for_status()
            session_url = r.json()["url"]
            self.checkoutSessionCreated.emit(session_url)
            logger.debug(f"Stripe Checkout session created: {session_url}")
            if callback and callback.isCallable():
                callback.call([session_url])
        except Exception as e:
            logger.error(f"Stripe Checkout Session Creation Failed: {e}")
            self.errorOccurred.emit(f"Failed to create checkout session: {e}")

    # ----- Ticket Generation ----------------------------------------------
    @Slot(str, result=None)
    def generateTicket(self, ticket_type: str):
        """POST /generate -> emits ticketGenerated"""
        if not self._auth_header:
            logger.debug("generateTicket called without auth token")
            self.errorOccurred.emit("No auth token available.")
            return
        url = f"{self.base_url}/generate"
        headers = {"Authorization": self._auth_header}
        data = {"ticket_type": ticket_type}
        logger.debug("generateTicket request to %s with type=%s", url, ticket_type)
        try:
            r = requests.post(url, json=data, headers=headers, timeout=8)
            logger.debug("generateTicket response status=%d", r.status_code)
            r.raise_for_status()
            payload = r.json().get("payload", "")
            logger.debug("generateTicket payload length=%d", len(payload))
            self.ticketGenerated.emit(payload)
        except Exception as e:
            logger.exception("Ticket generation failed for type %s", ticket_type)
            self.errorOccurred.emit(f"Ticket generation failed: {e}")

    # ----- Fetch ticket list ----------------------------------------------
    @Slot(result=None)
    def fetchTickets(self):
        """GET /wallet -> updates ticketList & emits ticketsFetched"""
        if not self._auth_header:
            logger.debug("fetchTickets called without auth token")
            self.errorOccurred.emit("No auth token available.")
            return
        url = f"{self.base_url}/wallet"
        headers = {"Authorization": self._auth_header}
        logger.debug("fetchTickets request to %s", url)
        try:
            r = requests.get(url, headers=headers, timeout=8)
            logger.debug("fetchTickets response status=%d", r.status_code)
            r.raise_for_status()
            tickets = r.json()
            logger.debug(f"Tickets: {tickets}")
            logger.debug("fetchTickets received %d tickets", len(tickets))
            self._ticket_list = tickets
            self.ticketsFetched.emit(self._ticket_list)
        except Exception as e:
            logger.exception("Fetch tickets failed")
            self.errorOccurred.emit(f"Fetch tickets failed: {e}")

    # ----- Load QR image ---------------------------------------------------
    @Slot(str, result=None)
    def loadQRCode(self, ticket_id: str):
        """GET /qr/{ticket_id} -> returns PNG as base64 data string"""
        if not self._auth_header:
            logger.debug("loadQRCode called without auth token")
            self.errorOccurred.emit("No auth token available.")
            return
        url = f"{self.base_url}/qr/{ticket_id}"
        headers = {"Authorization": self._auth_header}
        logger.debug("loadQRCode request to %s", url)
        try:
            r = requests.get(url, headers=headers, timeout=8)
            logger.debug("loadQRCode response status=%d, content-length=%s", r.status_code, r.headers.get("Content-Length"))
            r.raise_for_status()
            self._qr_image = "data:image/png;base64," + base64.b64encode(r.content).decode()
            logger.debug("loadQRCode image encoded, length=%d", len(self._qr_image))
        except Exception as e:
            logger.exception("Load QR code failed for ticket_id %s", ticket_id)
            self.errorOccurred.emit(f"Load QR failed: {e}")

