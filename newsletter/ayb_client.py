"""Minimal Python HTTP client for ayb (https://github.com/marcua/ayb)."""

import json
import os
import re
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
    def from_url(cls, url, token):
        match = re.match(r"^(https?://[^/]+)(?:/v1)?/([^/]+)/([^/]+)$", url)
        if not match:
            raise ValueError(f"Cannot parse ayb database URL: {url}")
        return cls(match.group(1), match.group(2), match.group(3), token)

    @classmethod
    def from_env(cls):
        return cls.from_url(os.environ["AYB_API_URL"], os.environ["AYB_TOKEN"])

    @staticmethod
    def escape(value):
        return str(value).replace("'", "''")

    @classmethod
    def sql_literal(cls, value):
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, int):
            return str(value)
        return "'" + cls.escape(value) + "'"

    def query(self, sql, retries=3):
        url = f"{self.base_url}/v1/{self.entity}/{self.database}/query"
        data = sql.encode("utf-8")
        delay = 1
        last_err = None
        for attempt in range(1, retries + 1):
            req = urllib.request.Request(
                url, data=data, method="POST",
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
                detail = exc.read().decode("utf-8", "replace")
                raise AybError(f"ayb query failed ({exc.code}): {detail}") from exc
            except urllib.error.URLError as exc:
                last_err = exc
                if attempt < retries:
                    time.sleep(delay)
                    delay *= 2
        raise AybError(f"ayb query failed after {retries} attempt(s): {last_err}")

    def rows(self, sql):
        result = self.query(sql)
        fields = result.get("fields", [])
        return [dict(zip(fields, row)) for row in result.get("rows", [])]

    def migrate(self, app_id, migrations):
        app = self.escape(app_id)
        self.query(
            "CREATE TABLE IF NOT EXISTS _ayb_migrations ("
            "app_id TEXT NOT NULL, version INTEGER NOT NULL, "
            "applied_at TEXT DEFAULT CURRENT_TIMESTAMP, "
            "PRIMARY KEY (app_id, version))"
        )
        rows = self.rows(
            f"SELECT MAX(version) as v FROM _ayb_migrations WHERE app_id = '{app}'"
        )
        current = 0
        if rows and rows[0]["v"] is not None:
            current = int(rows[0]["v"])
        for index in range(current, len(migrations)):
            self.query(migrations[index])
            self.query(
                "INSERT OR REPLACE INTO _ayb_migrations (app_id, version) "
                f"VALUES ('{app}', {index + 1})"
            )
        return len(migrations) - current
