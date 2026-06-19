"""Minimal Python HTTP client for ayb (https://github.com/marcua/ayb).

ayb's query endpoint takes a raw SQL string as the request body — there is no
parameterized-query support — so every interpolated value MUST be rendered with
``sql_literal`` (or escaped with ``escape`` and wrapped in single quotes).
"""

import json
import os
import time
import urllib.error
import urllib.request


class AybError(RuntimeError):
    pass


class AybClient:
    def __init__(self, base_url, entity, database, token):
        self.base_url = base_url.rstrip("/")
        self.entity = entity
        self.database = database
        self.token = token

    @classmethod
    def from_env(cls):
        base_url = os.environ["AYB_URL"]
        token = os.environ["AYB_TOKEN"]
        database = os.environ["AYB_DATABASE"]
        # AYB_DATABASE may be the full "entity/database" slug, or just the
        # database with AYB_ENTITY supplied separately.
        if "/" in database:
            entity, database = database.split("/", 1)
        else:
            entity = os.environ["AYB_ENTITY"]
        return cls(base_url, entity, database, token)

    # --- SQL value rendering (no parameterized queries in ayb) -------------- #
    @staticmethod
    def escape(value):
        """Escape a string for safe use *inside single quotes* in SQL."""
        return str(value).replace("'", "''")

    @classmethod
    def sql_literal(cls, value):
        """Render a Python value as a SQL literal."""
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, int):
            return str(value)
        return "'" + cls.escape(value) + "'"

    # --- Requests ---------------------------------------------------------- #
    def query(self, sql, retries=3):
        url = f"{self.base_url}/v1/{self.entity}/{self.database}/query"
        data = sql.encode("utf-8")
        delay = 1
        last_err = None
        for attempt in range(1, retries + 1):
            req = urllib.request.Request(
                url,
                data=data,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "text/plain",
                },
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    body = resp.read()
                    return json.loads(body) if body else {"fields": [], "rows": []}
            except urllib.error.HTTPError as exc:
                # 4xx/5xx from ayb: surface immediately, don't retry blindly.
                detail = exc.read().decode("utf-8", "replace")
                raise AybError(f"ayb query failed ({exc.code}): {detail}") from exc
            except urllib.error.URLError as exc:
                last_err = exc
                if attempt < retries:
                    time.sleep(delay)
                    delay *= 2
        raise AybError(f"ayb query failed after {retries} attempt(s): {last_err}")

    def rows(self, sql):
        """Run a query and return rows as dicts keyed by column name."""
        result = self.query(sql)
        fields = result.get("fields", [])
        return [dict(zip(fields, row)) for row in result.get("rows", [])]

    # --- Migrations -------------------------------------------------------- #
    def migrate(self, app_id, migrations):
        """Apply append-only DDL migrations, tracked per app in _ayb_migrations.

        ``migrations`` is a list of single-statement SQL strings; a migration's
        version is its 1-based index. Returns the number of migrations applied.
        """
        app = self.escape(app_id)
        self.query(
            "CREATE TABLE IF NOT EXISTS _ayb_migrations ("
            "app_id TEXT NOT NULL, version INTEGER NOT NULL, "
            "applied_at TEXT DEFAULT CURRENT_TIMESTAMP, "
            "PRIMARY KEY (app_id, version))"
        )
        result = self.query(
            f"SELECT MAX(version) FROM _ayb_migrations WHERE app_id = '{app}'"
        )
        rows = result.get("rows", [])
        current = 0
        if rows and rows[0] and rows[0][0] is not None:
            current = int(rows[0][0])
        for index in range(current, len(migrations)):
            self.query(migrations[index])
            self.query(
                "INSERT OR REPLACE INTO _ayb_migrations (app_id, version) "
                f"VALUES ('{app}', {index + 1})"
            )
        return len(migrations) - current
