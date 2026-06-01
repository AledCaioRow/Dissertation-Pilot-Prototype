---
tags: [concept]
---
# One-shot, Two-call Interaction

"One-shot" = **one human turn**, not one API call. Behind a single participant submit:

1. **Call 1** (differs by condition) builds the clarification interface —
   [[Call 1 Interface Generation]] (C2 detect / C3 generate).
2. *The participant interacts and submits once.*
3. **Call 2** generates SQL, [[Run SQL]] executes it locally, and the rows are fed back so
   the model writes its explanation **after** seeing the result — [[Call 2 Query Generation]].

There is no call 3: the post-execution explanation is folded into call 2.

**Key points**
- The participant sees, together: result rows, the generated SQL, and the explanation
  ([[Overreliance Probe]]).
- The grounding context (schema card + question) is built once by [[Build Context]] and
  reused across conditions — that's what isolates the variable.
- [[Conditions C1 C2 C3]]: C1 is the offline, no-human baseline (analysis only).

**Connected**
- [[The Experiment C2 vs C3]] · [[Main API]] (`/trial/interface`, `/trial/answer`)
- [[model_prompts]] — the call-2 prompt with `{rows_sample}` / `{row_count}`
