---
tags: [backend]
---
# Conditions — C1 / C2 / C3

Thin orchestration modules. Call 2 is shared, so a condition module only owns its call-1 step
(plus C1, which is offline).

**Code:** [`backend/conditions/`](../../backend/conditions) (`c1_baseline.py`, `c2_static.py`, `c3_bespoke.py`)

## How it works (plain English)
1. **C2** `run_interface(context, use_stub)` → runs [[Call 1 Interface Generation]] in detect mode →
   the fixed [[C2 Static Interface]].
2. **C3** `run_interface(context, use_stub)` → runs call 1 in generate mode → the [[C3 Dynamic Host]]
   live-mounts the returned JSX.
3. Both then share [[Call 2 Query Generation]] — the only between-condition difference is call 1.
4. **C1** `run_baseline(db, question, use_stub)` answers a question with **no human and no
   explanation** (one call → SQL → execute). It is **not** in the live session — the
   [[Analysis Notebook]] runs it post-hoc as the model-alone baseline.

**Connected:** [[The Experiment C2 vs C3]] · [[Counterbalancing]] (which question → which condition) · [[Main API]]
