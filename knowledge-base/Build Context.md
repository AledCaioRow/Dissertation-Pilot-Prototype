---
tags: [backend]
---
# Build Context

Builds the shared context (schema card + question) once and reuses it for every condition —
the structural guarantee that isolates the experimental variable.

**Code:** [`backend/context/build_context.py`](../backend/context/build_context.py)

**Key points**
- `build_context(db_name, question) -> Context{db_name, question, schema_card}`.
- `format_clarifications(responses)` renders the shared responses contract as
  `- <label>: <value>` lines for [[Call 2 Query Generation]].
- Uses [[Schema and Schema Card]]; the only per-condition difference is the call-1 instruction.

**Connected**
- [[One-shot Two-call Interaction]] · [[Conditions C1 C2 C3]] · [[CLAUDE_CODE_BRIEF]] §3
