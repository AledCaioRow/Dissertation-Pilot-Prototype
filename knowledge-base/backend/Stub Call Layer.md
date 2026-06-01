---
tags: [backend]
---
# Stub Call Layer

The single entry point every handler uses for a model completion. While stubbed it returns
canned, correctly-shaped payloads (`.content[0].text`, `.usage`); the one branch that changes to
go live is marked `# TODO: replace stub with real Anthropic call`.

**Code:** [`backend/calls/_stub.py`](../../backend/calls/_stub.py)

## How it works (plain English)
1. `complete(kind=…, prompt=…, use_stub=…)` is called for every model step.
2. It decides stub-vs-live from the **per-session** `use_stub` (page 0); if not given, it falls
   back to the config default.
3. **Stub branch:** it picks a canned payload by `kind` and returns it wrapped to look exactly like
   a real Anthropic message (same `.content`/`.usage` shape), with a tenacity retry wrapper.
4. **Live branch (the TODO):** it would call the real Anthropic Messages API with the key from
   `backend/.env`; same return shape, so callers don't change.
5. Canned payloads: C2 widgets; a **realistic, db-specific C3 interface** (a `top schools` control
   set for california_schools, a date-range/transaction set for financial); query SQL (table-free so
   it runs without the BIRD DBs); the post-execution explanation; and the C1 baseline SQL.

**Connected:** [[Call 1 Interface Generation]] · [[Call 2 Query Generation]] · [[Conditions C1 C2 C3]] · [[Stub vs Live]] · [[C3 Dynamic Host]]
