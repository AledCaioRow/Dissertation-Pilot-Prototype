---
tags: [backend]
---
# Counterbalancing

Deterministic `participant_id -> Assignment`, computed data-driven from the configured databases.

**Code:** [`backend/counterbalance/assign.py`](../../backend/counterbalance/assign.py)

## How it works (plain English)
1. Three crossed factors: the order the databases are shown, which condition block runs first
   (`C2,C3` or reversed), and a "slot pattern" deciding which class in each database is C2 vs C3.
2. With two databases that's 2×2×2 = **8** balanced assignments; the participant's id mod 8 picks one
   (add a third database and it scales to 24, no code change).
3. The result lists the four authored questions in order, each tagged with its **one** condition —
   so every participant gets exactly **two C2 and two C3** questions (4 trials; confirmed design).
4. `describe(a)` prints a human-readable summary for the start-of-session check; `all_assignments()`
   reproduces the whole table for the notebook.

**Key points**
- Each authored question is run **once**, under its assigned condition (not both) — see [[The Experiment C2 vs C3]].

**Connected:** [[Ambiguity Classes]] · [[Conditions C1 C2 C3]] · [[Wizard App]] (builds the screen order) · [[Config]]
