---
tags: [backend, moc]
---
# Backend Overview

FastAPI app, organised **by model call** so the call structure is self-evident on disk.
Thin endpoints delegate to conditions/handlers; every write persists the per-session log.

**Code:** [`backend/`](../backend) · entry point [[Main API]] (`backend/main.py`)

**Map**
- Tunables → [[Config]]
- Grounding → [[Schema and Schema Card]] → [[Build Context]]
- Execution → [[Run SQL]] (real, local SQLite)
- Model calls → [[Stub Call Layer]] → [[Call 1 Interface Generation]] · [[Call 2 Query Generation]]
- Orchestration → [[Conditions C1 C2 C3]] · [[Counterbalancing]]
- Records → [[Logging]]

**Key points**
- The numbered call folders (`01_…`, `02_…`) aren't valid module names, so they're loaded by
  path — see the loader in [`backend/calls/__init__.py`](../backend/calls/__init__.py).
- Stubbed model, real everything else — see [[Stub vs Live]].

**Connected**
- [[Frontend Overview]] (the client) · [[CLAUDE_CODE_BRIEF]] §5–§9
