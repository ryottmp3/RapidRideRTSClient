import requests
import logging
from PySide6.QtCore import QObject, Signal, Slot


class AdminStore(QObject):
    alertSent = Signal(bool, str)

    def __init__(self, auth_store):
        super().__init__()
        self.auth = auth_store
        self.logger = logging.getLogger("rts.client.admin")

    @Slot(str)
    def sendAlert(self, message):
        headers = {"Authorization": f"Bearer {self.auth.get_access_token()}"}
        try:
            r = requests.post(
                f"{self.auth.api_url}/alerts",
                json={"message": message},
                headers=headers
            )
            if r.status_code == 200:
                self.alertSent.emit(True, "Alert sent.")
            else:
                self.alertSent.emit(False, r.text)
        except Exception as e:
            self.alertSent.emit(False, f"Failed: {e}")
