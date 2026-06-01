"""REAL local SQLite execution — not an API call.

Structured as a standalone, reusable, *tool-shaped* function because in this design it
is used mid-call: call 2 generates SQL, `run_sql` executes it, and the rows are fed back
so the model writes its explanation against the actual result (build brief §8).
`RUN_SQL_TOOL_SPEC` is the Anthropic tool-use schema, ready to register when going live.

Read-only, with a hard timeout (worker thread + interrupt). Displayed rows are trimmed
to SHOW_RESULT_ROW_LIMIT; the true row_count is preserved for logging.

Smoke test (build order step 3):  python -m backend.execution.run_sql
"""
from __future__ import annotations

import sqlite3
import threading
from typing import Any, Optional

from pydantic import BaseModel

from backend import config


class ExecutionResult(BaseModel):
    success: bool
    rows: list[list[Any]]        # trimmed to SHOW_RESULT_ROW_LIMIT for display
    column_names: list[str]
    error: Optional[str] = None
    row_count: int = 0           # TRUE number of rows the query returned


RUN_SQL_TOOL_SPEC: dict[str, Any] = {
    "name": "run_sql",
    "description": (
        "Execute a single read-only SQLite query against the named database and return "
        "the resulting rows. Use this to see the actual result before explaining it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "db_name": {"type": "string", "description": "Configured database name."},
            "sql": {"type": "string", "description": "A single SQLite SELECT/WITH query."},
        },
        "required": ["db_name", "sql"],
    },
}


def _coerce(value: Any) -> Any:
    """Make a cell JSON-serialisable (BLOBs -> a short marker)."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return f"<{len(bytes(value))} bytes>"
    return value


def run_sql(db_name: str, sql: str) -> ExecutionResult:
    """Run `sql` against `db_name` read-only, with a timeout. Never raises for SQL errors."""
    try:
        path = config.db_path(db_name)
    except KeyError as exc:
        return ExecutionResult(success=False, rows=[], column_names=[], error=str(exc))

    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    except sqlite3.OperationalError as exc:
        return ExecutionResult(
            success=False,
            rows=[],
            column_names=[],
            error=f"Could not open database {db_name!r} read-only ({exc}). "
            f"Is {path} present? See bird_data/README.md.",
        )

    box: dict[str, Any] = {}

    def _work() -> None:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            box["columns"] = [d[0] for d in cur.description] if cur.description else []
            box["rows"] = cur.fetchall()
        except Exception as exc:  # noqa: BLE001 — surface any SQL/engine error as a string
            box["error"] = str(exc)

    worker = threading.Thread(target=_work, daemon=True)
    worker.start()
    worker.join(timeout=config.SQL_EXECUTION_TIMEOUT_SECONDS)

    if worker.is_alive():
        conn.interrupt()           # ask SQLite to abort the running statement
        worker.join(1.0)
        conn.close()
        return ExecutionResult(
            success=False,
            rows=[],
            column_names=[],
            error=f"Query exceeded {config.SQL_EXECUTION_TIMEOUT_SECONDS}s timeout.",
        )

    conn.close()

    if "error" in box:
        return ExecutionResult(success=False, rows=[], column_names=[], error=box["error"])

    all_rows: list[tuple] = box.get("rows", [])
    columns: list[str] = box.get("columns", [])
    trimmed = [[_coerce(v) for v in row] for row in all_rows[: config.SHOW_RESULT_ROW_LIMIT]]
    # Empty result is a success.
    return ExecutionResult(
        success=True,
        rows=trimmed,
        column_names=columns,
        error=None,
        row_count=len(all_rows),
    )


def rows_as_text(result: ExecutionResult, limit: int = 20) -> str:
    """First ~`limit` rows rendered as readable text for the call-2 explanation step."""
    if not result.success:
        return f"(query failed: {result.error})"
    if not result.rows:
        return "(no rows returned)"
    header = " | ".join(result.column_names)
    body = "\n".join(
        " | ".join("" if v is None else str(v) for v in row)
        for row in result.rows[:limit]
    )
    return f"{header}\n{body}"


if __name__ == "__main__":  # smoke test
    for db in config.DATABASES:
        print(f"\n===== {db} =====")
        res = run_sql(db, "SELECT 1 AS one, 'ok' AS status")
        print("trivial SELECT:", res.model_dump())
        res2 = run_sql(
            db,
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' LIMIT 5",
        )
        print("tables:", res2.rows if res2.success else res2.error)
