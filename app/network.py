# Updated Network.py

from wallet_store import WalletStore
import json
from datetime import datetime as dt
import logging
import requests
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QJSValue

logger = logging.getLogger("rts.network")

class NetworkManager(QObject):
    loginFinished = Signal(bool, str)
    registerFinished = Signal(bool, str)
    ticketGenerated = Signal(str)
    ticketsFetched = Signal('QVariantList')
    errorOccurred = Signal(str)
    checkoutSessionCreated = Signal(str)
    ticketListChanged = Signal()

    def __init__(self, base_url: str = "http://127.0.0.1:8000", auth_store=None):
        super().__init__()
        self.base_url = base_url
        self.auth_store = auth_store
        self._ticket_list: list[dict] = []
        self._wallet = WalletStore()
        self._wallet.walletUpdated.connect(self._onWalletUpdated)
        logger.debug("NetworkManager initialized with base_url=%s", self.base_url)

    def _onWalletUpdated(self, tickets):
        self._ticket_list = [
            {
                "ticket_id": self._extract_ticket_info(t, "ticket_id"),
                "ticket_type": self._extract_ticket_info(t, "ticket_type"),
                "status": self._extract_ticket_info(t, "status"),
                "issued_at": dt.fromisoformat(
                    self._extract_ticket_info(t, "issued_at")
                ).strftime("%d %B %Y, %I:%M %p"),
                "valid_for": self._format_valid_for(
                    self._extract_ticket_info(t, "valid_for")
                )
            } for t in tickets
        ]
        for t in self._ticket_list:
            logger.debug(f"Ticket in summary list: {t}")
        self.ticketListChanged.emit()

    def _extract_ticket_info(self, t, info: str):
        payload = t["payload"]
        return json.loads(payload)[info] if isinstance(payload, str) else payload[info]

    def _format_valid_for(self, value: str) -> str:
        try:
            if not value or value == "None":
                return "Any time"
            dt_obj = dt.strptime(value, "%Y-%m")
            return dt_obj.strftime("%B %Y")
        except Exception:
            return "None"

    @Slot(result=bool)
    def isLoggedIn(self) -> bool:
        logged_in = self.auth_store and self.auth_store.is_logged_in()
        logger.debug("isLoggedIn called, result=%s", logged_in)
        return logged_in

    def _get_ticket_list(self):
        logger.debug("Network._get_ticket_list called.")
        return self._ticket_list

    ticketList = Property("QVariant", _get_ticket_list, notify=ticketListChanged)

    @Slot(str, "QJSValue", result=None)
    def createCheckoutSession(self, ticket_type: str, callback: QJSValue = None):
        token = self.auth_store.get_access_token()
        if not token:
            self.errorOccurred.emit("You must be logged in.")
            return

        url = f"{self.base_url}/create-checkout-session"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            logger.debug("Creating Stripe Checkout Session")
            r = requests.post(url, json={"ticket_type": ticket_type}, headers=headers, timeout=8)

            if r.status_code == 401 and self.auth_store.refresh_tokens():
                logger.debug("Access token expired. Retrying after refresh.")
                token = self.auth_store.get_access_token()
                headers = {"Authorization": f"Bearer {token}"}
                r = requests.post(url, json={"ticket_type": ticket_type}, headers=headers, timeout=8)

            r.raise_for_status()
            session_url = r.json()["url"]
            self.checkoutSessionCreated.emit(session_url)
            logger.debug(f"Stripe Checkout session created: {session_url}")
            if callback and callback.isCallable():
                callback.call([session_url])
        except Exception as e:
            logger.error(f"Stripe Checkout Session Creation Failed: {e}")
            self.errorOccurred.emit(f"Failed to create checkout session: {e}")

    @Slot(str, str, result=None)
    def generateTicket(self, ticket_type: str, valid_for: str = ""):
        token = self.auth_store.get_access_token()
        if not token:
            logger.debug("generateTicket called without auth token")
            self.errorOccurred.emit("No auth token available.")
            return
        url = f"{self.base_url}/generate"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"ticket_type": ticket_type, "valid_for": valid_for}
        logger.debug("generateTicket request to %s with type=%s", url, ticket_type)
        try:
            r = requests.post(url, json=data, headers=headers, timeout=8)
            if r.status_code == 401 and self.auth_store.refresh_tokens():
                token = self.auth_store.get_access_token()
                headers = {"Authorization": f"Bearer {token}"}
                r = requests.post(url, json=data, headers=headers, timeout=8)
            r.raise_for_status()
            payload = r.json().get("payload", "")
            logger.debug("generateTicket payload length=%d", len(payload))
            self.ticketGenerated.emit(payload)
        except Exception as e:
            logger.exception("Ticket generation failed for type %s", ticket_type)
            self.errorOccurred.emit(f"Ticket generation failed: {e}")

    @Slot(result=None)
    def fetchTickets(self):
        token = self.auth_store.get_access_token()
        if not token:
            logger.debug("fetchTickets called without auth token")
            self.errorOccurred.emit("No auth token available.")
            return
        url = f"{self.base_url}/wallet"
        headers = {"Authorization": f"Bearer {token}"}
        logger.debug("fetchTickets request to %s", url)
        try:
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 401 and self.auth_store.refresh_tokens():
                token = self.auth_store.get_access_token()
                headers = {"Authorization": f"Bearer {token}"}
                r = requests.get(url, headers=headers, timeout=8)
            r.raise_for_status()
            server_ticket_dicts = r.json()
            self._wallet.syncWithServer(server_ticket_dicts)
        except Exception as e:
            logger.exception("Fetch tickets failed")
            self.errorOccurred.emit(f"Fetch tickets failed: {e}")

