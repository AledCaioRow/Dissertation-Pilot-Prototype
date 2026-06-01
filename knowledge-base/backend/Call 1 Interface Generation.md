---
tags: [backend, call]
---
# Call 1 — Interface Generation

The condition-specific first call: C2 detects ambiguities → multiple-choice clarification data;
C3 generates a bespoke interface + field manifest.

**Code:** [`backend/calls/01_interface_generation/`](../../backend/calls/01_interface_generation)
(`handler.py`, `io.py`, `prompt_c2_static.txt`, `prompt_c3_bespoke.txt`)

## How it works (plain English)
1. The handler loads the relevant prompt `.txt` at runtime and fills in the schema card + question
   (and, for C3, the list of allowed UI primitives so the prompt and the host can't drift).
2. It calls the model via [[Stub Call Layer]], passing the session's `use_stub` so the choice from
   page 0 decides stub vs live.
3. It takes the reply, strips any preamble (first `{` to last `}`), and validates it against the
   pydantic contract: `ClarificationData` for C2, `BespokeInterface` ({jsx, fields}) for C3.
4. If parsing fails it returns a safe default (empty widgets / empty interface) flagged
   `parsed_ok=false`, so the session never aborts — and records the raw reply.
5. It returns the validated object plus a call-log record (tokens, latency, the verbatim prompt).

**Connected:** [[Conditions C1 C2 C3]] · [[Stub Call Layer]] · [[AmbiSQL Static Interface]] · [[Dynamic Interface]] · [[Model Prompts]] · renders in [[C2 Static Interface]] / [[C3 Dynamic Host]]
