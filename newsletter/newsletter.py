"""Discover new blog posts from the Atom feed and email subscribers over SMTP.

Sending uses SMTP.
Subscribers, posts, and per-recipient send records live in an ayb database
(https://github.com/marcua/ayb). The ``sends`` table is the idempotency ledger:
a (post, subscriber) pair with status 'sent' is never emailed again.
"""

import contextlib
import os
import re
import smtplib
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage

from ayb_client import AybClient
from migrations import APP_ID, MIGRATIONS

BLOG_URL = os.environ.get("BLOG_URL", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
RATE_LIMIT_SECONDS = 0.6


# --------------------------------------------------------------------------- #
# SMTP
# --------------------------------------------------------------------------- #
def smtp_connection():
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]
    if port == 465:
        conn = smtplib.SMTP_SSL(host, port)
    else:
        conn = smtplib.SMTP(host, port)
        conn.starttls()
    conn.login(username, password)
    return conn


def unsubscribe_url(token):
    return f"{BLOG_URL}/newsletter/unsubscribe?token={urllib.parse.quote(token)}"


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


# --------------------------------------------------------------------------- #
# Feed parsing + email bodies
# --------------------------------------------------------------------------- #
def fetch_feed():
    blog_url = os.environ["BLOG_URL"]
    feed_url = f"{blog_url}/feed.xml"
    print(f"Fetching {feed_url}")
    with urllib.request.urlopen(urllib.request.Request(feed_url)) as resp:
        return resp.read().decode("utf-8")


def parse_feed(xml_text):
    """Return a list of post dicts: id, title, url, published, summary, html.

    ``id`` is the stable Atom <id> URI, also used as posts.feed_id in ayb.
    """
    root = ET.fromstring(xml_text)
    posts = []
    for entry in root.findall("atom:entry", ATOM_NS):
        post_id = (entry.findtext("atom:id", "", ATOM_NS) or "").strip()
        title = entry.findtext("atom:title", "", ATOM_NS) or ""
        link_el = entry.find("atom:link[@rel='alternate']", ATOM_NS)
        if link_el is None:
            link_el = entry.find("atom:link", ATOM_NS)
        url = link_el.get("href", "") if link_el is not None else ""
        published = entry.findtext("atom:published", "", ATOM_NS) or ""
        summary = (entry.findtext("atom:summary", "", ATOM_NS) or "").strip()
        content_el = entry.find("atom:content", ATOM_NS)
        html_content = (
            content_el.text if content_el is not None and content_el.text else ""
        )
        if post_id and published:
            posts.append(
                {
                    "id": post_id,
                    "title": title,
                    "url": url,
                    "published": published,
                    "summary": summary,
                    "html": html_content,
                }
            )
    return posts


def _normalize_text(value):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip().lower()


def _absolutify_urls(html, base_url):
    """Rewrite relative src= and href= attributes to absolute URLs."""
    def _rewrite(match):
        attr = match.group(1)
        quote = match.group(2)
        url = match.group(3)
        if url.startswith(("http://", "https://", "mailto:", "data:")):
            return match.group(0)
        absolute = base_url.rstrip("/") + "/" + url.lstrip("/")
        return f'{attr}={quote}{absolute}{quote}'
    return re.sub(r'(src|href|poster)=(["\'])(/[^"\']*)', _rewrite, html)


def _replace_videos(html, post_url):
    """Replace <video> tags with a linked poster image or a text link."""
    def _replace(match):
        tag = match.group(0)
        poster_match = re.search(r'poster=["\']([^"\']+)["\']', tag)
        if poster_match:
            poster = poster_match.group(1)
            return (
                f'<a href="{post_url}" style="display:block;text-align:center;">'
                f'<img src="{poster}" alt="Video thumbnail — click to watch" '
                f'style="max-width:100%;border-radius:4px;" />'
                f'</a>'
            )
        return f'<p><a href="{post_url}">▶ Watch video on blog</a></p>'
    return re.sub(r"<video[^>]*>[\s\S]*?</video>", _replace, html, flags=re.IGNORECASE)


def _constrain_images(html):
    """Add max-width:100% to all <img> tags so they don't overflow in email."""
    return re.sub(
        r"<img(?![^>]*max-width)",
        '<img style="max-width:100%;height:auto;"',
        html,
        flags=re.IGNORECASE,
    )


def _prepare_html_for_email(html, post_url, base_url):
    html = _absolutify_urls(html, base_url)
    html = _replace_videos(html, post_url)
    html = _constrain_images(html)
    return html


def build_html_email(title, url, summary, html_content):
    subtitle_html = ""
    if summary:
        summary_norm = _normalize_text(summary)
        content_norm = _normalize_text(html_content)
        prefix_len = min(len(summary_norm), 60)
        if summary_norm and summary_norm[:prefix_len] != content_norm[:prefix_len]:
            subtitle_html = f'<p style="color:#555;font-style:italic;">{summary}</p>\n'
    view_link = f'<p><a href="{url}">View on blog</a></p>\n'
    body = _prepare_html_for_email(html_content, url, BLOG_URL)
    footer = (
        f'<hr style="margin-top:2em;border:none;border-top:1px solid #ccc;">'
        f'<p style="font-size:0.9em;color:#666;">'
        f"You're receiving this because you subscribed at "
        f'<a href="{BLOG_URL}">{BLOG_URL}</a>.<br>'
        f'<a href="{{{{UNSUBSCRIBE_URL}}}}">Unsubscribe</a></p>'
    )
    return (
        f"<h1>{title}</h1>\n"
        f"{subtitle_html}"
        f"{view_link}"
        f"{body}\n"
        f"{footer}"
    )


def build_text_email(post):
    body = f"{post['title']}\n\n"
    if post["summary"] and len(post["summary"]) <= 200:
        body += f"{post['summary']}\n\n"
    body += f"Read more: {post['url']}\n"
    body += "\n---\n"
    body += f"You're receiving this because you subscribed at {BLOG_URL}.\n"
    body += "To unsubscribe: {{UNSUBSCRIBE_URL}}"
    return body


# --------------------------------------------------------------------------- #
# ayb data access
# --------------------------------------------------------------------------- #
def fetch_eligible_recipients(client, post_id, published_date):
    """Return subscribers who confirmed on or before published_date and
    haven't already been sent this post."""
    pub = AybClient.sql_literal(published_date)
    return client.rows(
        f"SELECT s.id, s.email, s.secret_token FROM subscribers s "
        f"WHERE s.confirmed_at IS NOT NULL "
        f"AND s.unsubscribed_at IS NULL "
        f"AND DATETIME(s.confirmed_at) <= DATETIME({pub}) "
        f"AND s.id NOT IN ("
        f"  SELECT subscriber_id FROM sends "
        f"  WHERE post_id = {int(post_id)}"
        f") ORDER BY s.id"
    )


def upsert_post(client, post):
    client.query(
        "INSERT OR IGNORE INTO posts (feed_id, url, title, published_at) VALUES ("
        f"{AybClient.sql_literal(post['id'])}, "
        f"{AybClient.sql_literal(post['url'])}, "
        f"{AybClient.sql_literal(post['title'])}, "
        f"{AybClient.sql_literal(post['published'])})"
    )
    rows = client.rows(
        f"SELECT id FROM posts WHERE feed_id = {AybClient.sql_literal(post['id'])}"
    )
    return int(rows[0]["id"])


def record_send(client, post_id, subscriber_id, status, error=None):
    client.query(
        "INSERT OR REPLACE INTO sends (post_id, subscriber_id, status, error) "
        f"VALUES ({int(post_id)}, {int(subscriber_id)}, "
        f"{AybClient.sql_literal(status)}, {AybClient.sql_literal(error)})"
    )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def send_admin_summary(run_results):
    if not ADMIN_EMAIL or not run_results:
        return
    total_sent = sum(r["sent"] for r in run_results)
    total_failed = sum(len(r["failed_emails"]) for r in run_results)

    lines = [f"Newsletter run complete: {len(run_results)} post(s) sent.\n"]
    for r in run_results:
        lines.append(f"- {r['title']}: {r['sent']}/{r['total']} delivered")
        for addr in r["failed_emails"]:
            lines.append(f"    FAILED: {addr}")
    lines.append(f"\nTotal: {total_sent} sent, {total_failed} failed.")

    subject = f"Newsletter: {total_sent} sent"
    if total_failed:
        subject += f", {total_failed} failed"

    conn = smtp_connection()
    try:
        conn.send_message(build_message(ADMIN_EMAIL, subject, "\n".join(lines)))
    finally:
        with contextlib.suppress(Exception):
            conn.quit()
    print("Admin summary sent.")


def main():
    client = AybClient.from_env()
    applied = client.migrate(APP_ID, MIGRATIONS)
    if applied:
        print(f"Applied {applied} migration(s).")

    posts = parse_feed(fetch_feed())
    if not posts:
        print("No posts found in feed.")
        return

    existing_posts = client.rows("SELECT COUNT(*) as n FROM posts")
    is_cold_start = int(existing_posts[0]["n"]) == 0

    for post in posts:
        post["db_id"] = upsert_post(client, post)

    if is_cold_start:
        print(f"Cold start: recorded {len(posts)} existing post(s); no emails sent.")
        return

    run_results = []
    conn = smtp_connection()
    try:
        for post in sorted(posts, key=lambda p: p["published"]):
            recipients = fetch_eligible_recipients(
                client, post["db_id"], post["published"]
            )
            if not recipients:
                continue

            text_tmpl = build_text_email(post)
            html_tmpl = (
                build_html_email(post["title"], post["url"], post["summary"], post["html"])
                if post["html"]
                else None
            )

            sent_count = 0
            failed_emails = []
            for sub in recipients:
                unsub = unsubscribe_url(sub["secret_token"])
                text_body = text_tmpl.replace("{{UNSUBSCRIBE_URL}}", unsub)
                html_body = (
                    html_tmpl.replace("{{UNSUBSCRIBE_URL}}", unsub) if html_tmpl else None
                )
                msg = build_message(sub["email"], post["title"], text_body, html_body, unsub)
                try:
                    conn.send_message(msg)
                    record_send(client, post["db_id"], sub["id"], "sent")
                    sent_count += 1
                except Exception as exc:
                    failed_emails.append(sub["email"])
                    record_send(client, post["db_id"], sub["id"], "failed", str(exc))
                    print(f"    ERROR sending to a subscriber: {type(exc).__name__}")
                time.sleep(RATE_LIMIT_SECONDS)

            run_results.append(
                {
                    "title": post["title"],
                    "sent": sent_count,
                    "total": len(recipients),
                    "failed_emails": failed_emails,
                }
            )
            line = f"  '{post['title']}': sent {sent_count}/{len(recipients)}"
            if failed_emails:
                line += f", {len(failed_emails)} failed"
            print(line)
    finally:
        with contextlib.suppress(Exception):
            conn.quit()

    send_admin_summary(run_results)


if __name__ == "__main__":
    main()
