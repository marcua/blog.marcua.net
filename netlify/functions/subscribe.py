import contextlib
import json
import os
import secrets
import smtplib
import urllib.parse
from email.message import EmailMessage

from _ayb import ayb_query, ayb_rows, sql_literal

FROM_EMAIL = os.environ.get("FROM_EMAIL", "")
REPLY_TO = os.environ.get("REPLY_TO", "")
BLOG_NAME = "N=1 (marcua's blog)"
BLOG_URL = "https://blog.marcua.net"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}


def _send_confirmation(email, unsub_url):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    msg["Subject"] = f"You're subscribed to {BLOG_NAME}"
    if REPLY_TO:
        msg["Reply-To"] = REPLY_TO
    msg["List-Unsubscribe"] = f"<{unsub_url}>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(
        f"Thank you for subscribing! You'll get an email whenever "
        f"I publish a new post.\n\n"
        f"Visit the blog: {BLOG_URL}\n\n"
        f"To unsubscribe: {unsub_url}"
    )

    if port == 465:
        smtp = smtplib.SMTP_SSL(host, port)
    else:
        smtp = smtplib.SMTP(host, port)
        smtp.starttls()
    try:
        smtp.login(username, password)
        smtp.send_message(msg)
    finally:
        with contextlib.suppress(Exception):
            smtp.quit()


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Method not allowed"}),
        }

    try:
        body = json.loads(event.get("body", "{}"))
    except (json.JSONDecodeError, TypeError):
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Invalid JSON"}),
        }

    email = (body.get("email") or "").strip()
    if not email or "@" not in email:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "A valid email is required"}),
        }

    try:
        token = secrets.token_urlsafe(32)

        # Re-subscribe if previously unsubscribed, otherwise insert new.
        existing = ayb_rows(
            f"SELECT id, unsubscribed_at FROM subscribers "
            f"WHERE email = {sql_literal(email)}"
        )
        if existing:
            ayb_query(
                f"UPDATE subscribers SET unsubscribed_at = NULL, "
                f"unsubscribe_token = {sql_literal(token)} "
                f"WHERE id = {int(existing[0]['id'])}"
            )
        else:
            ayb_query(
                f"INSERT INTO subscribers (email, unsubscribe_token) "
                f"VALUES ({sql_literal(email)}, {sql_literal(token)})"
            )

        unsub_url = (
            f"{BLOG_URL}/.netlify/functions/unsubscribe"
            f"?token={urllib.parse.quote(token)}"
        )
        _send_confirmation(email, unsub_url)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"ok": True}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }
