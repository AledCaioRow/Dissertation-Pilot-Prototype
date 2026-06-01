---
tags: [backend, moc]
---
# Backend Overview

FastAPI app, organised **by model call** so the call structure is self-evident on disk. Thin
endpoints delegate to conditions/handlers; every write persists the per-session log. Runs
locally on the researcher's laptop.

**Code:** [`backend/`](../../backend) · entry point [[Main API]] (`backend/main.py`)

## How it works (plain English)
1. The frontend talks to one FastAPI app; each request is keyed by `participant_id`.
2. Work is split into two model "calls", each its own folder under `backend/calls/` — call 1
   builds the clarification interface, call 2 writes + runs + explains the SQL.
3. Those folders are named `01_…`/`02_…`, which aren't valid Python module names, so a tiny
   loader imports their `handler.py`/`io.py` by file path and caches them.
4. Whether a call is stubbed or live is decided **per session** (page 0) and threaded down.
5. After every step the endpoint saves the whole session to one JSON file, so a crash resumes.

## Map
- Tunables → [[Config]]; grounding → [[Schema and Schema Card]] → [[Build Context]]
- Execution → [[Run SQL]]; model calls → [[Stub Call Layer]] → [[Call 1 Interface Generation]] · [[Call 2 Query Generation]]
- Orchestration → [[Conditions C1 C2 C3]] · [[Counterbalancing]]; records → [[Logging]]

**Connected:** [[Frontend Overview]] (the client) · [[Build Brief]] §5–§9 · [[Stub vs Live]]
