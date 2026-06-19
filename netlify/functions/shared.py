"""Shared SMTP and blog constants for both Netlify functions and newsletter."""

import contextlib
import os
import smtplib
import urllib.parse
from email.message import EmailMessage

BLOG_NAME = "N=1 (marcua's blog)"
BLOG_URL = "https://blog.marcua.net"


def smtp_connection():
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]
    if port == 465:
        smtp = smtplib.SMTP_SSL(host, port)
    else:
        smtp = smtplib.SMTP(host, port)
        smtp.starttls()
    smtp.login(username, password)
    return smtp


def send_smtp(msg):
    """Send a single EmailMessage over SMTP."""
    conn = smtp_connection()
    try:
        conn.send_message(msg)
    finally:
        with contextlib.suppress(Exception):
            conn.quit()


def unsubscribe_url(token):
    return f"{BLOG_URL}/.netlify/functions/unsubscribe?token={urllib.parse.quote(token)}"


def build_message(to, subject, text_body, html_body=None, list_unsubscribe=None):
    from_email = os.environ.get("FROM_EMAIL", "")
    reply_to = os.environ.get("REPLY_TO", "")
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    if list_unsubscribe:
        msg["List-Unsubscribe"] = f"<{list_unsubscribe}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")
    return msg
