---
tags: [backend]
---
# Logging

One JSON file per participant (`session_logs/p{ID}.json`), written incrementally so a crash can
resume from the last logged phase. Local files on the laptop.

**Code:** [`backend/logging_io/session_log.py`](../../backend/logging_io/session_log.py) ·
[`backend/logging_io/call_log.py`](../../backend/logging_io/call_log.py)

## How it works (plain English)
1. `SessionLog` holds the assignment, the page-0 `use_stub` choice, consent, screening, the list of
   `trials`, the per-condition questionnaires, the debrief, and `withdrawn`/`complete` flags.
2. Each `Trial` holds the generated interface, the participant's responses, the result (rows, SQL,
   explanation), the two-stage `perceived_success`, the C3 `compile_success`, and one
   `CallLogRecord` per model call.
3. `CallLogRecord` captures tokens, latency, the verbatim prompt, the raw reply, and parse/compile
   flags — the inputs to the cost comparison.
4. Every endpoint loads the session, mutates it, and saves it **atomically** (write temp + replace),
   so the file on disk is always consistent.

**Connected:** [[Main API]] (mutates + saves on every write) · [[Analysis Notebook]] (loads these) · [[Config]]
