# Wallet Store: Manages local storage of tickets
import json
import base64
import logging
import requests
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, QStandardPaths
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class WalletStore(QObject):
    """
    Persistent wallet storage with ticket validation and debug logging.
    Stores tickets in wallet.json under AppDataLocation.
    Loads ED25519 public key from ConfigLocation or app directory,
    or fetches it from server.
    Signals:
      - walletLoaded(list): emitted after initial load
      - walletUpdated(list): emitted after add/clear
    """
    walletLoaded = Signal(list)
    walletUpdated = Signal(list)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("rts.client.walletstore")
        self.logger.debug("Initializing WalletStore")

        # Determine storage paths
        data_dir = QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation
        )
        cfg_dir = QStandardPaths.writableLocation(
            QStandardPaths.ConfigLocation
        )
        self._file = Path(data_dir) / "wallet.json"
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        self.logger.debug("Data directory: %s", data_dir)
        self.logger.debug("Config directory: %s", cfg_dir)

        # Locate or fetch public key
        pubkey_path = None
        search_paths = [
            Path(cfg_dir) / "public_key.pem",
            Path(__file__).parent / "public_key.pem"
        ]
        for p in search_paths:
            if p.exists():
                pubkey_path = p
                self.logger.debug("Using public key at %s", p)
                break
        if not pubkey_path:
            # Fetch from server
            base_url = os.getenv("API_URL", "http://127.0.0.1:8000")
            key_url = f"{base_url}/public_key"
            try:
                self.logger.debug("Fetching public key from %s", key_url)
                r = requests.get(key_url, timeout=5)
                r.raise_for_status()
                pem = r.content
                target = Path(cfg_dir) / "public_key.pem"
                Path(cfg_dir).mkdir(parents=True, exist_ok=True)
                target.write_bytes(pem)
                pubkey_path = target
                self.logger.debug("Fetched and saved public key to %s", target)
            except Exception as e:
                self.logger.error(
                    "Failed to fetch public key from server: %s",
                    e
                )
                raise FileNotFoundError(
                    f"Missing public key and cannot fetch from server: {e}"
                )

        # Load public key
        raw_key = pubkey_path.read_bytes()
        self._pubkey = Ed25519PublicKey.from_public_bytes(raw_key)
        self.logger.debug("Loaded ED25519 public key from %s", pubkey_path)

        # Internal ticket list
        self._tickets = []
        self.load()

    def load(self):
        """Load wallet.json, validate each payload, emit walletLoaded."""
        self.logger.debug("Loading wallet from %s", self._file)
        if self._file.exists():
            data = json.loads(self._file.read_text())
            valid = []
            for ticket in data:
                payload = ticket.get("payload", "")
                signature = ticket.get("signature", "")
                if self.validateTicket(payload, signature):
                    valid.append(ticket)
                else:
                    self.logger.warning(
                        "Invalid ticket dropped: %s...",
                        payload
                    )
            self._tickets = valid
        else:
            self.logger.debug("Wallet file does not exist, starting empty")
            self._tickets = []
        self.walletLoaded.emit(self._tickets)
        self.logger.debug(
            "Emitted walletLoaded with %d tickets",
            len(self._tickets)
        )

    def save(self):
        """Write current tickets to disk and emit walletUpdated."""
        self.logger.debug(
            "Saving %d tickets to %s",
            len(self._tickets),
            self._file
        )
        # self.logger.debug(f"Saving tickets as: {self._tickets}")
        self._file.write_text(json.dumps(self._tickets, indent=2))
        self.walletUpdated.emit(self._tickets)
        self.logger.debug("Emitted walletUpdated")

    def validateTicket(self, payload: str, sig: str) -> bool:
        """
        Verify ED25519 signature appended to payload bytes.
        Assumes payload is base64(message||signature).
        """
        try:
            self.logger.debug(f"\n PAYLOAD TO VALIDATE: \n {payload}\n")
            self.logger.debug(f"\n SIGNATURE FOR VALIDATION: \n {sig}\n")
            # msg = base64.b64decode(json.loads(payload))
            # self.logger.debug(f" \n DECODED PAYLOAD: \n {msg} \n")
            ticket_json = self.serialize_ticket(payload).encode()
            self._pubkey.verify(base64.b64decode(sig), ticket_json)
            self.logger.debug("\n PAYLOAD VERIFICATION SUCCESSFUL\n")
            return True
        except Exception as e:
            self.logger.debug("validateTicket failed: %s", e)
            return False

    def serialize_ticket(self, ticket: dict) -> str:
        """Canonical JSON Format -- sorted keys, no whitespace"""
        return json.dumps(ticket, separators=(',', ':'), sort_keys=True)

    @Slot(str)
    def addTicket(self, payload: str):
        """Validate and append a new ticket."""
        for msg, sig in self.generatePayload(payload):
            if not self.validateTicket(msg, sig):
                self.logger.error("Payload failed validation, not adding")
                return
            ticket = {
                "payload": msg,
                "signature": sig
            }
            self.logger.debug(f"addTicket adding: {ticket}")
            self._tickets.append(ticket)
            self.save()

    @Slot("QVariantList")
    def addMultipleTickets(self, ticket_dicts):
        for payload, sig in self.generatePayload(ticket_dicts):
            self.logger.debug("Validation Payload: %s", payload)
            if not self.validateTicket(payload, sig):
                self.logger.error("Payload validation failed, not adding")
                continue
            self.logger.debug(f"addMultipleTickets adding payload: {payload}")
            self._tickets.append({"payload": payload, "signature": sig})
        self.save()

    @Slot(int)
    def deleteTicket(self, ticket_id: str):
        """Remove a ticket by its ID and save."""
        self._tickets = [
            t for t in self._tickets
            if json.loads(t["payload"]).get("ticked_id") != ticket_id
        ]
        self.save()

    @Slot()
    def clearWallet(self):
        """Remove all tickets and delete the storage file."""
        self.logger.debug("Clearing wallet and deleting file %s", self._file)
        self._tickets = []
        if self._file.exists():
            self._file.unlink()
        self.walletUpdated.emit(self._tickets)

    @Slot(result=list)
    def getTickets(self) -> list:
        """Return list of summary dicts for QML: id, type, status"""
        self.logger.debug(
            "getTickets called, returning %d tickets",
            len(self._tickets)
        )
        return self._tickets

    def getTicketSummaries(self) -> list:
        summaries = []
        for entry in self._tickets:
            try:
                payload_json = entry["payload"]
                ticket = json.loads(payload_json)
                summaries.append({
                    "ticket_id": ticket.get("ticket_id"),
                    "ticket_type": ticket.get("ticket_type"),
                    "status": ticket.get("status")
                })
            except Exception as e:
                self.logger.error(f"Malformed ticket in wallet: {e}")
        return summaries

    def generatePayload(self, ticket_dicts):
        """
        Given a list of dicts from the server (each with a 'signature' field),
        yield exactly the base64(msg_bytes || sig_bytes) strings that
        validateTicket() expects.
        """
        for d in ticket_dicts:
            self.logger.debug(f"\nTicket Dict: {d}")
            sig_b64 = d["signature"]
            msg_dict = json.loads(d["ticket"])
            self.logger.debug(f"\n Ticket: {d["ticket"]}")

            yield msg_dict, sig_b64

    def dumpTicket(self, ticket):
        return json.dumps(ticket, separators=(',', ':'), sort_keys=False)

    def _extract_ticket_id(self, t):
        payload = t["payload"]
        return json.loads(payload)["ticket_id"] if isinstance(payload, str) else payload["ticket_id"]

    def syncWithServer(self, server_ticket_dicts: list[dict]):
        """
        Given fresh ticket dicts from the server, add new/updated tickets
        and remove any tickets no longer present
        """
        self.logger.debug(
            f"Starting syncWithServer with {
                len(server_ticket_dicts)
            } server tickets."
        )

        local_by_id = {
            self._extract_ticket_id(t): t
            for t in self._tickets
        }

        server_by_id = {
            json.loads(t["ticket"])["ticket_id"]: t
            for t in server_ticket_dicts
        }

        new_tickets = []
        for tid, server_ticket in server_by_id.items():
            sig = server_ticket["signature"]
            ticket_dict = json.loads(server_ticket["ticket"])
            if tid not in local_by_id:
                self.logger.debug("New ticket from server: %s", tid)
                if self.validateTicket(ticket_dict, sig):
                    new_tickets.append({
                        "payload": server_ticket["ticket"],
                        "signature": sig
                    })
            else:
                local_ticket = local_by_id[tid]
                # If signature changed → consider it updated
                if local_ticket["signature"] != sig:
                    self.logger.debug("Updated ticket from server: %s", tid)
                    if self.validateTicket(ticket_dict, sig):
                        new_tickets.append({
                            "payload": self.dumpTicket(ticket_dict),
                            "signature": sig
                        })

        # Remove tickets no longer present
        server_ids = set(server_by_id.keys())
        kept = []
        for t in self._tickets:
            tid = self._extract_ticket_id(t)
            if tid in server_ids:
                # self.logger.debug(f"syncWithServer adding ticket: {t}")
                kept.append(t)
            else:
                self.logger.debug("Removing stale ticket: %s", tid)

        # Add new/updated ones
        kept.extend(new_tickets)
        # self.logger.debug(f"syncWithServer extending _tickets with: {kept}")
        self._tickets = kept
        self.save()
