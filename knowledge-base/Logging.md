---
tags: [backend]
---
# Logging

One JSON file per participant (`session_logs/p{ID}.json`), written incrementally from phase 1
so a crash can resume from the last logged phase.

**Code:** [`backend/logging_io/session_log.py`](../backend/logging_io/session_log.py) ·
[`backend/logging_io/call_log.py`](../backend/logging_io/call_log.py)

**Key points**
- `SessionLog` holds assignment, consent, screening, `trials[]`, questionnaires, debrief,
  `withdrawn`/`complete`. `Trial` holds the interface, responses, result, `perceived_success`,
  `compile_success`, and a `CallLogRecord` per model call.
- `CallLogRecord`: tokens, latency, verbatim prompt (if `LOG_PROMPTS_VERBATIM`), raw response,
  `parsed_ok`, `compile_success` — the inputs to the cost comparison.
- Atomic writes (`.tmp` + replace).

**Connected**
- [[Main API]] (mutates + saves on every write) · [[Analysis Notebook]] (loads these) · [[Config]]
