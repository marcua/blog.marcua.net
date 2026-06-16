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
  so a retry within a day is a no-op for already-delivered recipients.
* A post is always recorded as sent after sending, even if some recipients fail.
  This prevents the scenario where a persistently-failing address causes every
  other subscriber to receive the email again after the 24h idempotency window.
  Failed recipients are logged for observability but do not block forward progress.
* State is checkpointed (written + committed + pushed) after each post.
"""

import hashlib
import json
import os
import re
import subprocess
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
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / ".sent_posts.json"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

RATE_LIMIT_SECONDS = 0.6
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
    seen = set()
    subscribers = []
    after = None
    while True:
        path = f"/audiences/{RESEND_AUDIENCE_ID}/contacts?limit=100"
        if after:
            path += f"&after={urllib.parse.quote(after)}"
        result = resend_api("GET", path)
        page = result.get("data", [])
        for contact in page:
            if not contact.get("unsubscribed", False):
                email = contact["email"]
                if email not in seen:
                    seen.add(email)
                    subscribers.append(email)
        if not page or not result.get("has_more"):
            break
        after = page[-1].get("id")
        if not after:
            break
    return subscribers


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
            print("    idempotent no-op (409)")
            return
        raise


# --------------------------------------------------------------------------- #
# Feed parsing
# --------------------------------------------------------------------------- #
def parse_feed(xml_text):
    """Return a list of post dicts: id, title, url, published, summary, html.

    Post IDs are the stable <id> URIs from the Atom feed, e.g.
    ``https://blog.marcua.net/2026/05/05/figmimic`` — the same format used
    as keys in .sent_posts.json.
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
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            f"{STATE_PATH} not found. Commit a seed .sent_posts.json to the repo."
        )
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
        return
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
        # Merge (not rebase) so a normal push always works without --force.
        _git("pull", "--no-rebase", "--autostash", "origin", branch, check=False)
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

    run_results = []
    for post in new_posts:
        text_body = build_text_email(post)
        html_body = (
            build_html_email(post["title"], post["url"], post["summary"], post["html"])
            if post["html"]
            else None
        )

        sent_count = 0
        failed = []
        for email in subscribers:
            try:
                send_email(email, post["title"], text_body, html_body, post["id"])
                sent_count += 1
            except Exception as exc:
                failed.append(email)
                print(f"    ERROR sending to a subscriber: {exc}")
            time.sleep(RATE_LIMIT_SECONDS)

        run_results.append({
            "title": post["title"],
            "sent": sent_count,
            "total": len(subscribers),
            "failed": failed,
        })

        result_msg = f"  '{post['title']}': sent {sent_count}/{len(subscribers)}"
        if failed:
            result_msg += f", {len(failed)} failed"
        print(result_msg)

        # Always record the post as sent. Failed recipients are logged but don't
        # block progress — this prevents the scenario where a persistently-failing
        # address causes everyone else to get duplicates after idempotency expires.
        state.add(post["id"])
        save_state(state)
        commit_state(f"chore: record newsletter send for {post['id']}")

    send_admin_summary(run_results)


def send_admin_summary(run_results):
    """Email the admin a summary of the run with failure details."""
    if not ADMIN_EMAIL or not run_results:
        return
    total_sent = sum(r["sent"] for r in run_results)
    total_failed = sum(len(r["failed"]) for r in run_results)
    total_recipients = sum(r["total"] for r in run_results)

    lines = [f"Newsletter run complete: {len(run_results)} post(s) processed.\n"]
    for r in run_results:
        lines.append(f"- {r['title']}: {r['sent']}/{r['total']} delivered")
        if r["failed"]:
            lines.append(f"  Failed addresses:")
            for addr in r["failed"]:
                lines.append(f"    {addr}")
    lines.append(f"\nTotal: {total_sent} sent, {total_failed} failed across {total_recipients} recipient(s).")

    subject = f"Newsletter: {total_sent} sent"
    if total_failed:
        subject += f", {total_failed} failed"

    resend_api("POST", "/emails", {
        "from": FROM_EMAIL,
        "to": [ADMIN_EMAIL],
        "subject": subject,
        "text": "\n".join(lines),
    })
    print("Admin summary sent.")


if __name__ == "__main__":
    main()
