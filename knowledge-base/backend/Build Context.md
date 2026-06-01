---
tags: [backend]
---
# Build Context

Builds the shared context (schema card + question) once and reuses it for every condition — the
structural guarantee that isolates the experimental variable.

**Code:** [`backend/context/build_context.py`](../../backend/context/build_context.py)

## How it works (plain English)
1. `build_context(db_name, question)` renders the schema card for that database and bundles it with
   the participant's question into one small `Context` object.
2. That same object is handed to whichever call runs next, so C1/C2/C3 all see identical grounding —
   the only thing that differs between conditions is the call-1 instruction.
3. There is **no hints layer**: the schema card carries everything (tables, columns, types, keys).
4. `format_clarifications(responses)` turns the participant's submitted answers into tidy
   `- <label>: <value>` lines for call 2's prompt (handling arrays and date ranges).

**Connected:** [[One-shot Two-call Interaction]] · [[Conditions C1 C2 C3]] · [[Schema and Schema Card]] · [[Build Brief]] §3
