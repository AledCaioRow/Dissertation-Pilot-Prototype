---
tags: [backend]
---
# Run SQL

REAL local SQLite execution — not an API call. Tool-shaped so it can be registered as an
Anthropic tool-use tool, because in this design it runs **mid-call 2** (generate → execute →
explain).

**Code:** [`backend/execution/run_sql.py`](../backend/execution/run_sql.py)

**Key points**
- `run_sql(db_name, sql) -> ExecutionResult {success, rows, column_names, error, row_count}`.
- Read-only open (`mode=ro`); hard timeout via worker thread + `interrupt()`.
- Displayed rows trimmed to `SHOW_RESULT_ROW_LIMIT`; true `row_count` preserved for [[Logging]].
- Empty result = success; SQL errors → `success=False` + message (the wizard shows a neutral note).
- `RUN_SQL_TOOL_SPEC` is the ready-to-register tool schema; `rows_as_text()` feeds the explanation.

**Connected**
- [[Call 2 Query Generation]] · [[Schema and Schema Card]] · [[Config]] (timeout, row limit)
