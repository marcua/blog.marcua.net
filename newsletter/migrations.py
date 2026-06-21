"""ayb schema for the newsletter, as an append-only list of DDL migrations.

Rules (matching the ayb migration convention):
* Each entry is a single idempotent SQL statement.
* A migration's version is its 1-based position in this list.
* Only ever APPEND. Never edit or reorder existing entries — to change the
  schema, add a new ALTER/CREATE statement at the end.
"""

APP_ID = "newsletter"

MIGRATIONS = [
    # 1: subscribers. Column originally named unsubscribe_token, renamed to
    # secret_token in migration 5.
    """CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        unsubscribe_token TEXT NOT NULL UNIQUE,
        subscribed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        unsubscribed_at TEXT
    )""",
    # 2: posts seen in the feed. feed_id is the stable Atom <id>.
    """CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_id TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        published_at TEXT NOT NULL,
        first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    # 3: the subscriber x post send ledger. UNIQUE(post_id, subscriber_id) plus
    # a status='sent' check is the idempotency guarantee (at-most-once per pair).
    """CREATE TABLE IF NOT EXISTS sends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL REFERENCES posts(id),
        subscriber_id INTEGER NOT NULL REFERENCES subscribers(id),
        status TEXT NOT NULL,
        error TEXT,
        sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (post_id, subscriber_id)
    )""",
    # 4: double opt-in. NULL = unconfirmed; only confirmed subscribers
    # (confirmed_at IS NOT NULL) receive the newsletter.
    "ALTER TABLE subscribers ADD COLUMN confirmed_at TEXT",
    # 5: rename unsubscribe_token -> secret_token (serves confirm + unsubscribe).
    "ALTER TABLE subscribers RENAME COLUMN unsubscribe_token TO secret_token",
]
