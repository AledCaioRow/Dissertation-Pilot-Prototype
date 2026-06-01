---
tags: [backend]
---
# Counterbalancing

Deterministic `participant_id -> Assignment`, computed data-driven from the configured
databases.

**Code:** [`backend/counterbalance/assign.py`](../backend/counterbalance/assign.py)

**Key points**
- Three crossed factors: `schema_order` (permutation of databases), `condition_block_order`
  (`[C2,C3]`/reverse), `slot_pattern` (which class-slot → C2 vs C3, applied uniformly).
- Two databases → 2×2×2 = **8** balanced assignments (`participant_id % 8`); each participant
  gets exactly two C2 and two C3 questions. Add a third database → 24, no code change.
- `describe()` prints the start-of-session check; `all_assignments()` reproduces the table in
  the [[Analysis Notebook]].
- Reconciles [[CLAUDE_CODE_BRIEF]] §9's "permutation of three / 24" (it assumed three schemas).

**Connected**
- [[Ambiguity Classes]] · [[Conditions C1 C2 C3]] · [[Wizard App]] (builds the screen order) · [[Config]]
