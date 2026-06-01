---
tags: [backend, call]
---
# Call 2 — Query Generation + Explanation

Shared by C2 and C3. Folds three steps into one logical call: generate `{interpretation, sql}` →
[[Run SQL]] executes it → the rows are fed back so the explanation is **post-execution**. There is
no call 3.

**Code:** [`backend/calls/02_query_generation/`](../../backend/calls/02_query_generation)
(`handler.py`, `io.py`, `prompt.txt`)

## How it works (plain English)
1. `generate_query(context, responses, use_stub=…)` formats the prompt with the schema card, the
   original question, and the participant's clarifications as `- label: value` lines.
2. **Step 1:** ask the model for an interpretation + SQL; `clean_sql` recovers the query if it came
   wrapped in prose.
3. **Step 2:** run that SQL locally via [[Run SQL]] (real execution).
4. **Step 3:** ask the model again, now giving it the actual rows + row count, to write a plain
   explanation that references the real result.
5. Return `{interpretation, sql, explanation}` plus the execution result and the call-log records
   (both model steps tagged as call 2). Going live, these become one tool-use completion.

**Connected:** [[One-shot Two-call Interaction]] · [[Overreliance Probe]] · [[Build Context]] (clarifications) · [[Stub Call Layer]] · [[Main API]] (`/trial/answer`) · [[Model Prompts]]
