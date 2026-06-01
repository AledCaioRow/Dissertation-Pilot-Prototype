---
tags: [backend]
---
# Main API

The FastAPI endpoints — thin, validating with pydantic and persisting the [[Logging|session log]]
on every write. State keyed by `participant_id`.

**Code:** [`backend/main.py`](../backend/main.py)

**Endpoints**
- `POST /session/start` → compute [[Counterbalancing|assignment]], create log.
- `POST /session/consent`, `/session/screening`, `POST /session/withdraw`.
- `GET /schema/{name}` → [[Schema and Schema Card]] JSON.
- `POST /author` → store an authored question as a stub trial (returns `trial_id`, condition).
- `POST /trial/interface` → run [[Call 1 Interface Generation]] (C2/C3).
- `POST /trial/answer` → [[Call 2 Query Generation]] (generate → [[Run SQL]] → explain); returns rows + SQL.
- `POST /trial/perceived`, `POST /questionnaire`, `POST /debrief`.
- `GET /config` → the few constants the frontend needs.

**Connected**
- [[Wizard App]] / [[API Client and Mock]] (the client) · [[Conditions C1 C2 C3]] · [[CLAUDE_CODE_BRIEF]] §6
