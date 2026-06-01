---
tags: [backend]
---
# Config

The primary tuning surface — every tunable parameter as a named constant.

**Code:** [`backend/config.py`](../backend/config.py)

**Key points**
- `USE_STUB` (the stub switch — [[Stub vs Live]]), `MODEL_NAME`, token/temperature, retries.
- `DATABASES` and `SCHEMA_CLASS_MAP` (drives [[Ambiguity Classes]] and [[Counterbalancing]]).
- `SHOW_RESULT_ROW_LIMIT`, `SQL_EXECUTION_TIMEOUT_SECONDS` ([[Run SQL]]),
  `QUESTION_AUTHORING_MIN_CHARS`, `LOADING_SCREEN_MIN_SECONDS` (surfaced via `/config`).
- `db_path()` / `session_log_dir()` helpers; `.sqlite` files live in `bird_data/` (git-ignored).

**Connected**
- [[Main API]] (`/config` exposes a subset to the frontend) · [[CLAUDE_CODE_BRIEF]] §7
