---
tags: [backend]
---
# Conditions — C1 / C2 / C3

Thin orchestration modules. Call 2 is shared, so a condition module only owns its call-1 step
(plus C1, which is offline).

**Code:** [`backend/conditions/`](../backend/conditions) — `c1_baseline.py`, `c2_static.py`, `c3_bespoke.py`

**Key points**
- **C2** `run_interface()` → [[Call 1 Interface Generation]] (detect) → [[C2 Static Interface]].
- **C3** `run_interface()` → [[Call 1 Interface Generation]] (generate) → [[C3 Dynamic Host]].
- **C1** `run_baseline(db, question)` — no human, no explanation; one call → SQL → [[Run SQL]].
  Run **post-hoc only** in the [[Analysis Notebook]].

**Connected**
- [[The Experiment C2 vs C3]] · [[Counterbalancing]] (which question → which condition) · [[Main API]]
