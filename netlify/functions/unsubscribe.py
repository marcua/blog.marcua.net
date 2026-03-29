import json
import os
import urllib.request
import urllib.error


RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID", "")
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

    email = (event.get("queryStringParameters") or {}).get("email", "").strip()
    if not email or "@" not in email:
        return {
            "statusCode": 400,
            "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
            "body": "<html><body><p>Invalid or missing email address.</p></body></html>",
        }

    try:
        # Find the contact ID for this email
        req = urllib.request.Request(
            f"https://api.resend.com/audiences/{RESEND_AUDIENCE_ID}/contacts",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            method="GET",
        )
        with urllib.request.urlopen(req) as resp:
            contacts = json.loads(resp.read()).get("data", [])

        contact = next((c for c in contacts if c["email"] == email), None)
        if contact is None:
            return {
                "statusCode": 200,
                "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
                "body": (
                    "<html><body>"
                    "<p>That email address was not found in our subscriber list.</p>"
                    "</body></html>"
                ),
            }

        # Update contact to unsubscribed
        data = json.dumps({"unsubscribed": True}).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.resend.com/audiences/{RESEND_AUDIENCE_ID}/contacts/{contact['id']}",
            data=data,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            method="PATCH",
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()

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
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {
            "statusCode": 500,
            "headers": {**CORS_HEADERS, "Content-Type": "text/html"},
            "body": (
                "<html><body>"
                "<p>Something went wrong. Please try again later.</p>"
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
