import json
import os

from _ayb import ayb_query, ayb_rows, sql_literal

BLOG_URL = "https://blog.marcua.net"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
}


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    if event.get("httpMethod") != "GET":
        return {
            "statusCode": 405,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Method not allowed"}),
        }

    token = (event.get("queryStringParameters") or {}).get("token", "").strip()
    if not token:
        return {
            "statusCode": 400,
            "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
            "body": "<html><body><p>Invalid or missing unsubscribe link.</p></body></html>",
        }

    try:
        rows = ayb_rows(
            f"SELECT id FROM subscribers "
            f"WHERE unsubscribe_token = {sql_literal(token)} "
            f"AND unsubscribed_at IS NULL"
        )
        if not rows:
            return {
                "statusCode": 200,
                "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
                "body": (
                    "<html><body>"
                    "<p>This unsubscribe link is not valid or you are already unsubscribed.</p>"
                    "</body></html>"
                ),
            }

        ayb_query(
            f"UPDATE subscribers SET unsubscribed_at = CURRENT_TIMESTAMP "
            f"WHERE id = {int(rows[0]['id'])}"
        )

        return {
            "statusCode": 200,
            "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
            "body": (
                "<html><body>"
                "<p>You've been unsubscribed. You won't receive any more emails.</p>"
                f'<p><a href="{BLOG_URL}">Back to blog</a></p>'
                "</body></html>"
            ),
        }
    except Exception:
        return {
            "statusCode": 500,
            "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
            "body": (
                "<html><body>"
                "<p>Something went wrong. Please try again later.</p>"
                "</body></html>"
            ),
        }
