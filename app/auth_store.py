# auth_store.py
import os
import json
import requests
import logging
from PySide6.QtCore import QObject, Slot, Signal

class AuthStore(QObject):
    loginStatusChanged = Signal(bool)
    loginFinished = Signal(bool, str)
    registerFinished = Signal(bool, str)
    errorOccurred = Signal(str)

    def __init__(self, api_url="http://127.0.0.1:8000"):
        super().__init__()
        self.api_url = api_url
        self.logger = logging.getLogger("rts.client.auth")
        self.token_path = os.path.expanduser("~/.rapidride_auth.json")
        self._tokens = self._load_tokens()

    def _load_tokens(self):
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning("Failed to load tokens: %s", e)
        return {}

    def _save_tokens(self):
        try:
            with open(self.token_path, "w") as f:
                json.dump(self._tokens, f)
        except Exception as e:
            self.logger.warning("Failed to save tokens: %s", e)

    def _clear_tokens(self):
        self._tokens = {}
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.loginStatusChanged.emit(False)

    def get_access_token(self):
        return self._tokens.get("access_token")

    def get_refresh_token(self):
        return self._tokens.get("refresh_token")

    def is_logged_in(self):
        if not self.get_access_token():
            return False
        return self._validate_token() or self.refresh_tokens()

    def _validate_token(self):
        try:
            headers = {"Authorization": f"Bearer {self.get_access_token()}"}
            r = requests.get(f"{self.api_url}/users/me", headers=headers)
            return r.status_code == 200
        except Exception as e:
            self.logger.warning("Token validation failed: %s", e)
            return False

    def refresh_tokens(self):
        rt = self.get_refresh_token()
        if not rt:
            self.logger.debug("No refresh token found")
            return False

        try:
            headers = {"Authorization": f"Bearer {rt}"}
            r = requests.post(f"{self.api_url}/refresh", headers=headers)
            if r.status_code == 200:
                tokens = r.json()
                self._tokens["access_token"] = tokens["access_token"]
                self._tokens["refresh_token"] = tokens["refresh_token"]
                self._save_tokens()
                self.loginStatusChanged.emit(True)
                self._fetch_user_info()
                return True
            else:
                self.logger.warning("Refresh failed: %s", r.text)
        except Exception as e:
            self.logger.warning("Refresh request failed: %s", e)

        self._clear_tokens()
        return False

    @Slot(str, str, "QVariant")
    def login(self, username, password, _):
        try:
            data = {"username": username, "password": password}
            r = requests.post(f"{self.api_url}/token", data=data)
            if r.status_code == 200:
                tokens = r.json()
                self._tokens["access_token"] = tokens["access_token"]
                self._tokens["refresh_token"] = tokens["refresh_token"]
                self._save_tokens()
                self.loginFinished.emit(True, "Login successful.")
                self.loginStatusChanged.emit(True)
                self._fetch_user_info()
            else:
                self.logger.warning("Login failed: %s", r.text)
                self.loginFinished.emit(False, "Invalid username or password.")
        except Exception as e:
            self.logger.warning("Login exception: %s", e)
            self.loginFinished.emit(False, str(e))

    @Slot(str, str, str, "QVariant")
    def register(self, username, email, password, _):
        try:
            payload = {"username": username, "email": email or None, "password": password}
            r = requests.post(f"{self.api_url}/register", json=payload)
            if r.status_code == 201:
                tokens = r.json()
                self._tokens["access_token"] = tokens["access_token"]
                self._tokens["refresh_token"] = tokens["refresh_token"]
                self._save_tokens()
                self.registerFinished.emit(True, "Account created. You are now logged in.")
                self.loginStatusChanged.emit(True)
            else:
                self.logger.warning("Registration failed: %s", r.text)
                self.registerFinished.emit(False, r.json().get("detail", "Registration error"))
        except Exception as e:
            self.logger.warning("Registration exception: %s", e)
            self.registerFinished.emit(False, str(e))

    @Slot()
    def logout(self):
        rt = self.get_refresh_token()
        if rt:
            try:
                headers = {"Authorization": f"Bearer {rt}"}
                requests.post(f"{self.api_url}/logout", headers=headers)
            except Exception as e:
                self.logger.warning("Logout request failed: %s", e)
        self._clear_tokens()

    def _fetch_user_info(self):
        try:
            headers = {"Authorization": f"Bearer {self.get_access_token()}"}
            r = requests.get(f"{self.api_url}/users/me", headers=headers)
            if r.status_code == 200:
                user_info = r.json()
                self._tokens["is_admin"] = user_info.get("is_admin", False)
                self._save_tokens()
                return True
        except Exception as e:
            self.logger.warning("Fetching user info failed: %s", e)
        return False

    @Slot(result=bool)
    def isAdmin(self):
        return self._tokens.get("is_admin", False)
