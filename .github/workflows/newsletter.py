"""Fetch RSS feed, find new posts, email subscribers via Resend."""

import json
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

BLOG_URL = os.environ["BLOG_URL"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
RESEND_AUDIENCE_ID = os.environ["RESEND_AUDIENCE_ID"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

LAST_SENT_PATH = Path(__file__).resolve().parents[2] / ".last_sent"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def resend_api(method, path, payload=None):
    url = f"https://api.resend.com{path}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_subscribers():
    result = resend_api("GET", f"/audiences/{RESEND_AUDIENCE_ID}/contacts")
    return [
        c["email"]
        for c in result.get("data", [])
        if not c.get("unsubscribed", False)
    ]


def strip_html(html_text):
    """Crude HTML-to-text: strip tags, decode entities."""
    text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_feed(xml_text):
    """Parse Atom feed, return list of (title, url, date, summary, html_content) newest-first."""
    root = ET.fromstring(xml_text)
    posts = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title = entry.findtext("atom:title", "", ATOM_NS)
        link_el = entry.find("atom:link[@rel='alternate']", ATOM_NS)
        if link_el is None:
            link_el = entry.find("atom:link", ATOM_NS)
        url = link_el.get("href", "") if link_el is not None else ""
        published = entry.findtext("atom:published", "", ATOM_NS)
        summary = entry.findtext("atom:summary", "", ATOM_NS) or ""
        content_el = entry.find("atom:content", ATOM_NS)
        html_content = content_el.text if content_el is not None and content_el.text else ""
        if published:
            posts.append((title, url, published, summary.strip(), html_content))
    return posts


def unsubscribe_url(email):
    return f"{BLOG_URL}/.netlify/functions/unsubscribe?email={urllib.parse.quote(email)}"


def send_email(to, subject, text_body, html_body=None):
    unsub_url = unsubscribe_url(to)
    payload = {
        "from": FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "text": text_body.replace("{{UNSUBSCRIBE_URL}}", unsub_url),
        "headers": {
            "List-Unsubscribe": f"<{unsub_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
    }
    if html_body:
        payload["html"] = html_body.replace("{{UNSUBSCRIBE_URL}}", unsub_url)
    resend_api("POST", "/emails", payload)


def build_html_email(title, url, html_content):
    """Wrap post HTML content in a minimal email-safe wrapper."""
    footer = (
        f'<hr style="margin-top:2em;border:none;border-top:1px solid #ccc;">'
        f"<p style=\"font-size:0.9em;color:#666;\">"
        f"You're receiving this because you subscribed at "
        f'<a href="{BLOG_URL}">{BLOG_URL}</a>.<br>'
        f'<a href="{{{{UNSUBSCRIBE_URL}}}}">Unsubscribe</a></p>'
    )
    return (
        f"<h1>{title}</h1>\n"
        f"{html_content}\n"
        f'<p><a href="{url}">View on blog</a></p>\n'
        f"{footer}"
    )


def main():
    # 1. Fetch feed
    feed_url = f"{BLOG_URL}/feed.xml"
    print(f"Fetching {feed_url}")
    req = urllib.request.Request(feed_url)
    with urllib.request.urlopen(req) as resp:
        xml_text = resp.read().decode("utf-8")

    posts = parse_feed(xml_text)
    if not posts:
        print("No posts found in feed.")
        return

    # 2. Read last_sent
    if LAST_SENT_PATH.exists():
        last_sent = datetime.fromisoformat(LAST_SENT_PATH.read_text().strip())
    else:
        last_sent = datetime.min.replace(tzinfo=timezone.utc)
    print(f"Last sent: {last_sent.isoformat()}")

    # 3. Find new posts
    new_posts = []
    for title, url, published, summary, html_content in posts:
        pub_dt = datetime.fromisoformat(published)
        if pub_dt > last_sent:
            new_posts.append((title, url, pub_dt, summary, html_content))
    new_posts.sort(key=lambda p: p[2])  # oldest first

    if not new_posts:
        print("No new posts since last send.")
        return

    print(f"Found {len(new_posts)} new post(s).")

    # 4. Get subscribers
    subscribers = get_subscribers()
    if not subscribers:
        print("No subscribers found.")
        return
    print(f"Sending to {len(subscribers)} subscriber(s).")

    # 5. Send emails
    for title, url, pub_dt, summary, html_content in new_posts:
        text_body = f"{title}\n\n"
        if summary and len(summary) <= 200:
            text_body += f"{summary}\n\n"
        text_body += f"Read more: {url}\n"
        text_body += f"\n---\n"
        text_body += f"You're receiving this because you subscribed at {BLOG_URL}.\n"
        text_body += "To unsubscribe: {{UNSUBSCRIBE_URL}}"

        html_body = None
        if html_content:
            html_body = build_html_email(title, url, html_content)

        for email in subscribers:
            print(f"  Sending '{title}' to {email}")
            send_email(email, title, text_body, html_body)
            time.sleep(0.5)  # respect Resend rate limit

    # 6. Update .last_sent
    newest_dt = max(p[2] for p in new_posts)
    LAST_SENT_PATH.write_text(newest_dt.isoformat() + "\n")
    print(f"Updated .last_sent to {newest_dt.isoformat()}")


if __name__ == "__main__":
    main()
