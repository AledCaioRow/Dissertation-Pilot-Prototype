"""Executable content database — student_club, opened READ-ONLY.

The model is never given a live query tool; the frozen DB_CONTEXT is its only
value grounding. This module only runs the finaliser's SQL to fetch results,
and it refuses anything that is not a single SELECT.
"""

import os
import re
import sqlite3
from pathlib import Path

_HERE = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("STUDENT_CLUB_DB", _HERE / "data" / "student_club.sqlite"))

# Up to this many rows are previewed on the output screen; the full result is
# still stored for analysis.
PREVIEW_LIMIT = 15

# Statements/keywords that must never appear — defence in depth on top of the
# read-only connection.
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|create|alter|replace|pragma|attach|detach|"
    r"vacuum|reindex|truncate|grant|revoke|begin|commit|rollback)\b",
    re.IGNORECASE,
)


class SQLValidationError(ValueError):
    """Raised when a model query is not a single read-only SELECT."""


def _readonly_connection() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"student_club database not found at {DB_PATH}")
    # Immutable, read-only URI connection: the file cannot be written.
    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    # Belt and braces: reject any write attempt at the driver level too.
    conn.execute("PRAGMA query_only = ON;")
    return conn


def split_statements(sql: str) -> list:
    """Split a SQL string into individual statements on top-level semicolons.

    Single-quoted string literals (with doubled '' escapes) are respected so a
    ';' inside a literal does not split a statement. Blank fragments are dropped,
    so a trailing semicolon is harmless.
    """
    statements = []
    buf = []
    in_str = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        if ch == "'":
            buf.append(ch)
            if in_str and i + 1 < len(sql) and sql[i + 1] == "'":
                buf.append(sql[i + 1])  # escaped quote inside a literal
                i += 2
                continue
            in_str = not in_str
            i += 1
            continue
        if ch == ";" and not in_str:
            statements.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        statements.append("".join(buf))
    return [s.strip() for s in statements if s.strip()]


def validate_select(sql: str) -> str:
    """Return a cleaned single SELECT statement or raise SQLValidationError.

    The input must already be a single statement (no top-level ';'); use
    ``split_statements`` first when several may be present.
    """
    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL.")
    cleaned = sql.strip()
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()
    if ";" in cleaned:
        raise SQLValidationError("Each statement must be a single SELECT (found ';').")
    if "--" in cleaned or "/*" in cleaned:
        raise SQLValidationError("Comments are not allowed.")
    lowered = cleaned.lstrip("(").lstrip().lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise SQLValidationError("Only SELECT (or WITH ... SELECT) queries are allowed.")
    if _FORBIDDEN.search(cleaned):
        raise SQLValidationError("Query contains a forbidden write keyword.")
    return cleaned


def _run_one(conn, cleaned: str) -> dict:
    cur = conn.execute(cleaned)
    columns = [d[0] for d in cur.description] if cur.description else []
    rows = [dict(r) for r in cur.fetchall()]
    return {
        "sql": cleaned,
        "columns": columns,
        "rows": rows,                       # complete result, stored for analysis
        "preview_rows": rows[:PREVIEW_LIMIT],  # capped for the screen
        "total_count": len(rows),
    }


def run_queries(sql: str) -> list:
    """Validate and execute one or more SELECT statements read-only.

    Splits ``sql`` on top-level semicolons and runs each statement in order on a
    single read-only connection. Returns a list of result dicts, one per query,
    each with: sql, columns, rows, preview_rows, total_count.
    """
    statements = split_statements(sql)
    if not statements:
        raise SQLValidationError("Empty SQL.")
    results = []
    conn = _readonly_connection()
    try:
        for stmt in statements:
            results.append(_run_one(conn, validate_select(stmt)))
    finally:
        conn.close()
    return results


def run_select(sql: str):
    """Validate and execute a single SELECT read-only (backward-compatible).

    Returns (columns, all_rows, preview_rows, total_count). Prefer
    ``run_queries`` when more than one statement may be present.
    """
    conn = _readonly_connection()
    try:
        res = _run_one(conn, validate_select(sql))
    finally:
        conn.close()
    return res["columns"], res["rows"], res["preview_rows"], res["total_count"]
