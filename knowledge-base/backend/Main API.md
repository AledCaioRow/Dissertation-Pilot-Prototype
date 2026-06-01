---
tags: [backend]
---
# Main API

The FastAPI endpoints — thin, validating with pydantic and persisting the [[Logging|session log]]
on every write. State keyed by `participant_id`.

**Code:** [`backend/main.py`](../../backend/main.py)

## How it works (plain English)
1. `POST /session/start` computes the [[Counterbalancing|assignment]] and creates (or resumes) the log.
2. `POST /session/mode` records page 0's stub-vs-live choice on the session.
3. `POST /session/consent`, `/session/screening`, and `POST /session/withdraw` store those steps.
4. `GET /schema/{name}` returns the [[Schema and Schema Card|schema]] as JSON for the bland schema view.
5. `POST /author` saves one authored question (+ intent note) as a trial and returns its condition.
6. `POST /trial/interface` runs [[Call 1 Interface Generation]] for that trial's condition, passing
   the session's `use_stub`.
7. `POST /trial/answer` runs [[Call 2 Query Generation]] (generate → [[Run SQL]] → explain) and
   returns rows + SQL + explanation.
8. `POST /trial/perceived`, `/questionnaire`, `/debrief` store the ratings and close the session.
9. `GET /config` exposes the few constants (and the default mode) the frontend needs.

**Connected:** [[Wizard App]] / [[API Client]] (the client) · [[Conditions C1 C2 C3]] · [[Build Brief]] §6
