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


def validate_select(sql: str) -> str:
    """Return a cleaned single SELECT statement or raise SQLValidationError."""
    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL.")
    cleaned = sql.strip()
    # Strip any accidental trailing semicolon, but reject genuine 2nd statements.
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()
    if ";" in cleaned:
        raise SQLValidationError("Only one statement is allowed (found ';').")
    if "--" in cleaned or "/*" in cleaned:
        raise SQLValidationError("Comments are not allowed.")
    lowered = cleaned.lstrip("(").lstrip().lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise SQLValidationError("Only SELECT (or WITH ... SELECT) queries are allowed.")
    if _FORBIDDEN.search(cleaned):
        raise SQLValidationError("Query contains a forbidden write keyword.")
    return cleaned


def run_select(sql: str):
    """Validate and execute a SELECT read-only.

    Returns (columns, all_rows, preview_rows, total_count) where rows are lists
    of plain dicts. ``all_rows`` is the complete result (stored for analysis),
    ``preview_rows`` is capped at PREVIEW_LIMIT for the screen.
    """
    cleaned = validate_select(sql)
    conn = _readonly_connection()
    try:
        cur = conn.execute(cleaned)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    total = len(rows)
    preview = rows[:PREVIEW_LIMIT]
    return columns, rows, preview, total
