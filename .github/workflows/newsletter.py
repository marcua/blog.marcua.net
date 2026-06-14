"""Fetch the blog's Atom feed, find unsent posts, and email subscribers via Resend.

State model
----------
The set of already-emailed posts is stored in ``.sent_posts.json`` at the repo
root as a list of stable feed ``<id>`` values. Membership (``id not in sent``)
is the dedup test, which is immune to publication-date ties, back-dating, and
non-monotonic dates that a single "last sent" timestamp watermark would mishandle.

Delivery safety
---------------
* Each ``POST /emails`` carries a deterministic ``Idempotency-Key`` derived from
  ``(post_id, recipient)``. Resend dedupes identical keys server-side for ~24h,
  so a retry within a day re-sends only the recipients that didn't already get it.
* State is checkpointed (written + committed + pushed) after each post that sends
  cleanly, so a mid-run failure can't force a wholesale re-send of earlier posts.
* A post is only checkpointed when every recipient succeeded. If any send fails,
  the post is left unrecorded and the run exits non-zero; the next run retries it,
  with idempotency keys neutralizing the already-delivered recipients.

Cold start
----------
On the very first run (no state file), every post currently in the feed is
recorded as "already sent" and no email goes out, so the back-catalog is never
emailed. A seed file is also committed to the repo up front for the same reason;
the cold-start branch is a defensive net in case the state file ever goes missing.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BLOG_URL = os.environ["BLOG_URL"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
RESEND_AUDIENCE_ID = os.environ["RESEND_AUDIENCE_ID"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = REPO_ROOT / ".sent_posts.json"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

# Resend free tier allows 2 requests/second.
RATE_LIMIT_SECONDS = 0.5
# Network push retries use exponential backoff starting here.
PUSH_RETRY_BASE_SECONDS = 2
PUSH_RETRIES = 4


# --------------------------------------------------------------------------- #
# Resend API
# --------------------------------------------------------------------------- #
def resend_api(method, path, payload=None, extra_headers=None):
    url = f"https://api.resend.com{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        body = resp.read()
        return json.loads(body) if body else {}


def get_subscribers():
    """Return all non-unsubscribed contact emails, following pagination."""
    emails = []
    after = None
    while True:
        path = f"/audiences/{RESEND_AUDIENCE_ID}/contacts?limit=100"
        if after:
            path += f"&after={urllib.parse.quote(after)}"
        result = resend_api("GET", path)
        page = result.get("data", [])
        for contact in page:
            if not contact.get("unsubscribed", False):
                emails.append(contact["email"])
        if not page or not result.get("has_more"):
            break
        after = page[-1].get("id")
        if not after:
            break
    # De-dupe while preserving order, in case the same email appears twice.
    seen = set()
    unique = []
    for email in emails:
        if email not in seen:
            seen.add(email)
            unique.append(email)
    return unique


def idempotency_key(post_id, email):
    """Deterministic per-(post, recipient) key, <= 256 chars."""
    digest = hashlib.sha256(f"{post_id}\n{email}".encode("utf-8")).hexdigest()
    return f"newsletter/{digest}"


def unsubscribe_url(email):
    return f"{BLOG_URL}/.netlify/functions/unsubscribe?email={urllib.parse.quote(email)}"


def send_email(to, subject, text_body, html_body, post_id):
    unsub = unsubscribe_url(to)
    payload = {
        "from": FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "text": text_body.replace("{{UNSUBSCRIBE_URL}}", unsub),
        "headers": {
            "List-Unsubscribe": f"<{unsub}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
    }
    if html_body:
        payload["html"] = html_body.replace("{{UNSUBSCRIBE_URL}}", unsub)
    try:
        resend_api(
            "POST",
            "/emails",
            payload,
            extra_headers={"Idempotency-Key": idempotency_key(post_id, to)},
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            # Same idempotency key already in-flight or completed with the same
            # payload -> the email is already (being) sent. Treat as success.
            print(f"    idempotent no-op for {to} (409)")
            return
        raise


# --------------------------------------------------------------------------- #
# Feed parsing
# --------------------------------------------------------------------------- #
def parse_feed(xml_text):
    """Return a list of post dicts: id, title, url, published, summary, html."""
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
    """Strip HTML tags and collapse whitespace, lowercased, for comparison."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip().lower()


def build_html_email(title, url, summary, html_content):
    """Wrap post HTML content in a minimal email-safe wrapper.

    Show the summary as a subtitle line only when it isn't just the opening of
    the post body (i.e. an excerpt-based summary for a post with no subtitle).
    """
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
    # Posts without a subtitle fall back to the full first paragraph as the feed
    # summary, which reads poorly in plain text; only include short summaries.
    if post["summary"] and len(post["summary"]) <= 200:
        body += f"{post['summary']}\n\n"
    body += f"Read more: {post['url']}\n"
    body += "\n---\n"
    body += f"You're receiving this because you subscribed at {BLOG_URL}.\n"
    body += "To unsubscribe: {{UNSUBSCRIBE_URL}}"
    return body


# --------------------------------------------------------------------------- #
# State persistence
# --------------------------------------------------------------------------- #
def load_state():
    """Return the set of already-sent post ids, or None if there's no state."""
    if not STATE_PATH.exists():
        return None
    data = json.loads(STATE_PATH.read_text())
    return set(data.get("sent", []))


def save_state(sent_ids):
    STATE_PATH.write_text(json.dumps({"sent": sorted(sent_ids)}, indent=2) + "\n")


def _git(*args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def commit_state(message):
    """Commit and push .sent_posts.json. A no-op outside GitHub Actions."""
    if not os.environ.get("GITHUB_ACTIONS"):
        print("  (local run: skipping git commit/push of state)")
        return
    branch = os.environ.get("GITHUB_REF_NAME") or _git(
        "rev-parse", "--abbrev-ref", "HEAD"
    ).stdout.strip()
    _git("add", str(STATE_PATH))
    if _git("diff", "--staged", "--quiet", check=False).returncode == 0:
        return  # nothing to commit
    _git(
        "-c",
        "user.name=github-actions[bot]",
        "-c",
        "user.email=github-actions[bot]@users.noreply.github.com",
        "commit",
        "-m",
        f"{message} [skip ci]",
    )
    delay = PUSH_RETRY_BASE_SECONDS
    last_err = ""
    for attempt in range(1, PUSH_RETRIES + 1):
        _git("pull", "--rebase", "--autostash", "origin", branch, check=False)
        push = _git("push", "origin", f"HEAD:{branch}", check=False)
        if push.returncode == 0:
            return
        last_err = push.stderr.strip()
        print(f"  push attempt {attempt}/{PUSH_RETRIES} failed: {last_err}")
        if attempt < PUSH_RETRIES:
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"Failed to push state after {PUSH_RETRIES} attempts: {last_err}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def fetch_feed():
    feed_url = f"{BLOG_URL}/feed.xml"
    print(f"Fetching {feed_url}")
    with urllib.request.urlopen(urllib.request.Request(feed_url)) as resp:
        return resp.read().decode("utf-8")


def main():
    posts = parse_feed(fetch_feed())
    if not posts:
        print("No posts found in feed.")
        return

    state = load_state()
    if state is None:
        # Cold start: record every current post as sent so we never email the
        # back-catalog, and send nothing this run.
        seed = {post["id"] for post in posts}
        save_state(seed)
        commit_state(
            f"chore: seed newsletter state with {len(seed)} existing post(s)"
        )
        print(f"Cold start: seeded {len(seed)} existing post(s); no emails sent.")
        return

    new_posts = [post for post in posts if post["id"] not in state]
    new_posts.sort(key=lambda post: post["published"])  # oldest first
    if not new_posts:
        print("No new posts to send.")
        return
    print(f"Found {len(new_posts)} new post(s).")

    subscribers = get_subscribers()
    if not subscribers:
        print("No subscribers found.")
        return
    print(f"Sending to {len(subscribers)} subscriber(s).")

    for post in new_posts:
        text_body = build_text_email(post)
        html_body = (
            build_html_email(post["title"], post["url"], post["summary"], post["html"])
            if post["html"]
            else None
        )

        sent = 0
        failed = []
        for email in subscribers:
            try:
                send_email(email, post["title"], text_body, html_body, post["id"])
                sent += 1
            except Exception as exc:  # noqa: BLE001 - log and keep going
                failed.append(email)
                print(f"    ERROR sending to {email}: {exc}")
            time.sleep(RATE_LIMIT_SECONDS)

        summary = f"  '{post['title']}': sent {sent}/{len(subscribers)}"
        if failed:
            summary += f", {len(failed)} failed"
        print(summary)

        if failed:
            # Leave this post unrecorded so the next run retries it. Idempotency
            # keys make that retry a no-op for recipients already delivered
            # (within Resend's ~24h window). Stop here so we don't send newer
            # posts ahead of an older one that isn't fully delivered.
            sys.exit(
                f"{len(failed)} send(s) failed for '{post['title']}'; "
                f"state not advanced for it. Will retry next run."
            )

        state.add(post["id"])
        save_state(state)
        commit_state(f"chore: record newsletter send for {post['id']}")


if __name__ == "__main__":
    main()
