---
tags: [backend]
---
# Config

The primary tuning surface — every tunable parameter as a named constant.

**Code:** [`backend/config.py`](../../backend/config.py)

## How it works (plain English)
1. On import it loads `backend/.env` (so the Anthropic key stays in the backend, never the browser).
2. `USE_STUB` defaults from the env var `USE_STUB` (default true) — this is just the **default**
   that page 0's stub/live selector starts on; the per-session choice overrides it.
3. It holds the model name, token limits, temperature, retry settings, and the study constants:
   `DATABASES` (the two BIRD databases) and `SCHEMA_CLASS_MAP` (which ambiguity class each hosts).
4. It holds behaviour limits (display row cap, SQL timeout, authoring min-chars, loading-screen
   minimum) and the session-log directory.
5. Helpers resolve absolute paths: `db_path(name)` for a database file, `session_log_dir()`.

**Key points**
- Two databases only (california_schools, financial); four classes → [[Ambiguity Classes]], [[Counterbalancing]].
- `/config` exposes a small subset (incl. the default mode) to the frontend — see [[Main API]].

**Connected:** [[Stub vs Live]] · [[Schema and Schema Card]] · [[Build Brief]] §7
