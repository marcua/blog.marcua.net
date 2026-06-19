"""Discover new blog posts from the Atom feed and email subscribers over SMTP.

Sending uses SMTP.
Subscribers, posts, and per-recipient send records live in an ayb database
(https://github.com/marcua/ayb). The ``sends`` table is the idempotency ledger:
a (post, subscriber) pair with status 'sent' is never emailed again.
"""

import contextlib
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "netlify" / "functions"))

from ayb_client import AybClient
from migrations import APP_ID, MIGRATIONS
from shared import BLOG_URL, build_message, smtp_connection, unsubscribe_url

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
RATE_LIMIT_SECONDS = 0.6


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


def build_html_email(title, url, summary, html_content):
    subtitle_html = ""
    if summary:
        summary_norm = _normalize_text(summary)
        content_norm = _normalize_text(html_content)
        prefix_len = min(len(summary_norm), 60)
        if summary_norm and summary_norm[:prefix_len] != content_norm[:prefix_len]:
            subtitle_html = f'<p style="color:#555;font-style:italic;">{summary}</p>\n'
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
        f"{html_content}\n"
        f'<p><a href="{url}">View on blog</a></p>\n'
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
def fetch_active_subscribers(client):
    return client.rows(
        "SELECT id, email, unsubscribe_token FROM subscribers "
        "WHERE unsubscribed_at IS NULL ORDER BY id"
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


def already_sent_subscriber_ids(client, post_id):
    rows = client.rows(
        f"SELECT subscriber_id FROM sends WHERE post_id = {int(post_id)} "
        "AND status = 'sent'"
    )
    return {int(r["subscriber_id"]) for r in rows}


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
    for post in posts:
        post["db_id"] = upsert_post(client, post)

    subscribers = fetch_active_subscribers(client)
    if not subscribers:
        print("No active subscribers.")
        return
    print(f"{len(subscribers)} active subscriber(s).")

    run_results = []
    conn = smtp_connection()
    try:
        for post in sorted(posts, key=lambda p: p["published"]):
            already_sent = already_sent_subscriber_ids(client, post["db_id"])
            recipients = [s for s in subscribers if int(s["id"]) not in already_sent]
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
                unsub = unsubscribe_url(sub["unsubscribe_token"])
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
                    print(f"    ERROR sending to a subscriber: {exc}")
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
