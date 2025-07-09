# RapidRide Ticketing Client

This is the frontend client for the RapidRide fare system — a lightweight, secure, and mobile-friendly ticketing interface for public transit riders and fare inspectors.

The application is written using Qt/QML via PySide6 and supports secure QR code generation, Stripe-based ticket purchasing, and ticket validation scanning.

---

## 🖥️ Overview

RapidRide Client provides a modern desktop/mobile interface for purchasing and validating transit fare. The app is fully themeable, works offline, and includes an integrated QR scanner using OpenCV.

---

## 🛠️ Technology Stack

- **PySide6 (Qt for Python)** — cross-platform GUI framework
- **QML** — declarative UI markup
- **OpenCV + Pyzbar** — QR code scanning
- **Requests + dotenv** — backend communication
- **SQLite (local wallet)** — optional offline storage

---

## 🚧 Completed Milestones ✅

- [x] Theme-aware QML UI
- [x] QR code generation (signed ticket payload)
- [x] Ticket wallet with formatted ticket summaries
- [x] Stripe checkout integration
- [x] Camera-based QR scanner with overlay
- [x] Ed25519 signature verification support (via backend)
- [x] Ticket validation page with live server result
- [x] Page navigation system with controller binding

---

## 🎯 Upcoming Milestones 🔜

- [ ] Offline wallet + local-only validation fallback
- [ ] Fare inspector admin mode (tablet view)
- [ ] Multi-language support (English, Spanish, Lakota)
- [ ] Installer packaging (Windows, Android, AppImage)
- [ ] Session management + persistent login
- [ ] Refactor scanner as reusable module

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourname/rapidride-client.git
cd rapidride-client
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the client:

```bash
python main.py
```

Make sure the backend is running at the configured API URL (default: `http://127.0.0.1:8000`).

---

## ⚙️ Configuration

Update `.env` or pass environment variables to configure:

```dotenv
API_URL=http://127.0.0.1:8000
```

---

## 🧪 Development Notes

- PySide6-based code runs on Linux, Windows, and Android (experimental via `pyside6-deploy`)
- QML UI is modular and theme-driven
- You can connect to test/staging backends for multi-instance validation testing

---

## 📜 License

This project is licensed under the **GNU General Public License v3 (GPL-3.0)**. You are free to use, modify, and redistribute the code under the same license. All improvements to the core client must remain free and open.

---

## 👤 Author

Created and maintained by a solo developer as a civic technology project for municipalities like Rapid City, SD.  
Contact: harley.glayzer@mines.sdsmt.edu
