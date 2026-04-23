import json
import os
import ssl
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

import smtplib
from email.message import EmailMessage


ROOT = Path(__file__).resolve().parent

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5173"))

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
CONTACT_TO = os.environ.get("CONTACT_TO", GMAIL_USER)

SUBMISSIONS_PATH = ROOT / "contact-submissions.jsonl"


def is_valid_email(value: str) -> bool:
    v = (value or "").strip()
    return 5 <= len(v) <= 254 and "@" in v and " " not in v


def sanitize_text(value: str, max_len: int) -> str:
    v = (value or "").strip()
    return v[:max_len]


def can_send_email() -> bool:
    return bool(GMAIL_USER and GMAIL_APP_PASSWORD and CONTACT_TO)


def send_gmail(record: dict) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"New website contact: {record.get('name','')}"
    msg["From"] = f"Asset-Energy AI <{GMAIL_USER}>"
    msg["To"] = CONTACT_TO
    msg["Reply-To"] = record.get("email", "")

    text = (
        "New contact submission\n\n"
        f"Name: {record.get('name','')}\n"
        f"Email: {record.get('email','')}\n"
        f"Received: {record.get('receivedAt','')}\n"
        f"IP: {record.get('ip','')}\n"
        f"User-Agent: {record.get('ua','')}\n\n"
        "Message:\n"
        f"{record.get('message','')}\n"
    )
    msg.set_content(text)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/contact":
            self.send_error(404, "Not found")
            return

        length = int(self.headers.get("content-length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            payload = None

        name = sanitize_text((payload or {}).get("name", ""), 120)
        email = sanitize_text((payload or {}).get("email", ""), 254)
        message = sanitize_text((payload or {}).get("message", ""), 4000)

        if not name or not is_valid_email(email) or not message:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Invalid input"}).encode("utf-8"))
            return

        record = {
            "receivedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "name": name,
            "email": email,
            "message": message,
            "ip": self.client_address[0] if self.client_address else None,
            "ua": self.headers.get("user-agent"),
        }

        email_sent = False
        email_error = None
        if can_send_email():
            try:
                send_gmail(record)
                email_sent = True
            except Exception as e:
                email_error = str(e)

        # Always keep a local audit trail
        with SUBMISSIONS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps({**record, "emailSent": email_sent, "emailError": email_error}) + "\n")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "emailSent": email_sent}).encode("utf-8"))

    def do_GET(self):
        # Ensure the space-containing PNG filename works when requested by URL-encoded path.
        self.path = unquote(self.path)
        return super().do_GET()


def main():
    os.chdir(ROOT)
    port = PORT
    server = None
    last_err = None
    for _ in range(10):
        try:
            server = ThreadingHTTPServer((HOST, port), Handler)
            break
        except OSError as e:
            last_err = e
            port += 1

    if server is None:
        raise last_err  # type: ignore[misc]

    print(f"Landing page running on http://{HOST}:{port}")
    if not can_send_email():
        print("Gmail not configured. Set GMAIL_USER, GMAIL_APP_PASSWORD, and optional CONTACT_TO to enable sending.")
    server.serve_forever()


if __name__ == "__main__":
    main()

