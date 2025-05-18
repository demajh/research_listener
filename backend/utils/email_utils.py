# utils/email_utils.py
"""
Lightweight Gmail SMTP helper.
Uses an App-Password (recommended) or plain password if legacy account.
"""
import os
import ssl
import smtplib
from pathlib import Path
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT_SSL = 465                       # SSL on connection (simplest)

FROM_EMAIL = os.getenv("GMAIL_USER")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")   # 16-char app password


def _build_message(to_addr: str, subject: str, body_md: str, files: list[Path]) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_addr
    msg["Subject"] = subject

    # Plain-text + simple HTML (GitHub-style <pre>)
    msg.set_content(body_md)
    msg.add_alternative(f"<pre>{body_md}</pre>", subtype="html")

    for p in files:
        maintype, subtype = ("application", "pdf") if p.suffix == ".pdf" else ("text", "markdown")
        msg.add_attachment(
            p.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=p.name,
        )
    return msg


def send_email(to_email: str, subject: str, body_md: str, attachments: list[Path]):
    if not (FROM_EMAIL and APP_PASSWORD):
        raise RuntimeError("GMAIL_USER and GMAIL_APP_PASSWORD must be set")

    msg = _build_message(to_email, subject, body_md, attachments)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT_SSL, context=context) as server:
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.send_message(msg)

    print(f"  ✔ Email sent to {to_email}")
