---
tags: [backend, call]
---
# Call 2 — Query Generation + Explanation

Shared by C2 and C3. Folds three steps into one logical call: generate `{interpretation,
sql}` → [[Run SQL]] executes it → the rows are fed back so the explanation is **post-execution**.

**Code:** [`backend/calls/02_query_generation/`](../backend/calls/02_query_generation)
— `handler.py`, `io.py`, `prompt.txt`

**Key points**
- `generate_query(context, responses, condition) -> (QueryGenerationResult, ExecutionResult, [CallLogRecord])`.
- `clean_sql()` recovers SQL if the model wrapped it in prose (first ```sql block, else SELECT/WITH).
- Going live, the three steps become one tool-use completion with `run_sql` as the tool — no call 3.

**Connected**
- [[One-shot Two-call Interaction]] · [[Overreliance Probe]] · [[Build Context]] (clarifications)
- [[Stub Call Layer]] · [[Main API]] (`/trial/answer`) · [[model_prompts]] (call 2)
