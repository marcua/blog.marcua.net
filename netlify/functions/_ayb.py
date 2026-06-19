"""Shared ayb helpers for Netlify functions."""

import json
import os
import re
import urllib.error
import urllib.request


class AybError(RuntimeError):
    pass


def _parse_url(url):
    match = re.match(r"^(https?://[^/]+)(?:/v1)?/([^/]+)/([^/]+)$", url)
    if not match:
        raise ValueError(f"Cannot parse ayb database URL: {url}")
    return match.group(1), match.group(2), match.group(3)


def ayb_query(sql):
    """Run a SQL statement against the ayb database configured via env vars."""
    api_url = os.environ.get("AYB_API_URL", "")
    token = os.environ.get("AYB_TOKEN", "")
    if not api_url or not token:
        raise AybError("AYB_API_URL and AYB_TOKEN must be set")
    base_url, entity, database = _parse_url(api_url)
    url = f"{base_url}/v1/{entity}/{database}/query"
    data = sql.encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain",
        },
    )
    with urllib.request.urlopen(req) as resp:
        body = resp.read()
        return json.loads(body) if body else {"fields": [], "rows": []}


def ayb_rows(sql):
    """Run a query and return rows as dicts keyed by column name."""
    result = ayb_query(sql)
    fields = result.get("fields", [])
    return [dict(zip(fields, row)) for row in result.get("rows", [])]


def escape(value):
    """Escape a string for safe use inside single quotes in SQL."""
    return str(value).replace("'", "''")


def sql_literal(value):
    """Render a Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    return "'" + escape(value) + "'"
