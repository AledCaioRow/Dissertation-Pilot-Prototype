---
tags: [backend]
---
# Run SQL

REAL local SQLite execution — not an API call. Tool-shaped so it can be registered as an
Anthropic tool, because in this design it runs **mid-call 2** (generate → execute → explain).

**Code:** [`backend/execution/run_sql.py`](../../backend/execution/run_sql.py)

## How it works (plain English)
1. `run_sql(db_name, sql)` looks up the database file and opens it **read-only** (`mode=ro`).
2. It runs the query on a short-lived worker thread and waits up to a timeout; if it overruns,
   it interrupts the query and returns a timeout error instead of hanging.
3. On success it returns the column names, the rows (trimmed to the display cap), and the **true**
   row count; an empty result still counts as success.
4. Any SQL/engine error is caught and returned as `success=False` + a message (never raised), so
   the wizard can show a neutral note and carry on.
5. `rows_as_text(...)` renders the first rows as readable text for call 2's explanation step.

**Key points**
- `RUN_SQL_TOOL_SPEC` is the ready-to-register tool schema; missing DB files degrade gracefully.

**Connected:** [[Call 2 Query Generation]] · [[Schema and Schema Card]] · [[Config]] (timeout, row cap)
