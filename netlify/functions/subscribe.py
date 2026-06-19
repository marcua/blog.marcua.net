import json
import secrets
import urllib.parse

from ayb_client import AybClient
from shared import BLOG_NAME, BLOG_URL, build_message, send_smtp, unsubscribe_url

_client = None
sql_literal = AybClient.sql_literal

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}


def _get_client():
    global _client
    if _client is None:
        _client = AybClient.from_env()
    return _client


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
        client = _get_client()
        token = secrets.token_urlsafe(32)

        existing = client.rows(
            f"SELECT id, unsubscribed_at FROM subscribers "
            f"WHERE email = {sql_literal(email)}"
        )
        if existing:
            client.query(
                f"UPDATE subscribers SET unsubscribed_at = NULL, "
                f"unsubscribe_token = {sql_literal(token)} "
                f"WHERE id = {int(existing[0]['id'])}"
            )
        else:
            client.query(
                f"INSERT INTO subscribers (email, unsubscribe_token) "
                f"VALUES ({sql_literal(email)}, {sql_literal(token)})"
            )

        unsub = unsubscribe_url(token)
        msg = build_message(
            email,
            f"You're subscribed to {BLOG_NAME}",
            (
                f"Thank you for subscribing! You'll get an email whenever "
                f"I publish a new post.\n\n"
                f"Visit the blog: {BLOG_URL}\n\n"
                f"To unsubscribe: {unsub}"
            ),
            list_unsubscribe=unsub,
        )
        send_smtp(msg)

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
