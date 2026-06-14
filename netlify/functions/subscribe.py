import json
import os
import urllib.parse
import urllib.request
import urllib.error


RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "")
BLOG_NAME = "N=1 (marcua's blog)"
BLOG_URL = "https://blog.marcua.net"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}


def resend_request(path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.resend.com{path}",
        data=data,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


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
        # Add contact to audience
        resend_request("/contacts", {
            "email": email,
            "audience_id": RESEND_AUDIENCE_ID,
            "unsubscribed": False,
        })

        # Send confirmation email
        unsub_url = (
            f"{BLOG_URL}/.netlify/functions/unsubscribe"
            f"?email={urllib.parse.quote(email)}"
        )
        resend_request("/emails", {
            "from": FROM_EMAIL,
            "to": [email],
            "subject": f"You're subscribed to {BLOG_NAME}",
            "text": (
                f"Thank you for subscribing! You'll get an email whenever "
                f"I publish a new post.\n\n"
                f"Visit the blog: {BLOG_URL}\n\n"
                f"To unsubscribe: {unsub_url}"
            ),
            "headers": {
                "List-Unsubscribe": f"<{unsub_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        })

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"ok": True}),
        }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": f"Resend API error: {error_body}"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }
