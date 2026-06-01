---
tags: [backend, call]
---
# Call 1 — Interface Generation

The condition-specific first call: C2 detects ambiguities → multiple-choice clarification
data; C3 generates a bespoke interface + field manifest.

**Code:** [`backend/calls/01_interface_generation/`](../backend/calls/01_interface_generation)
— `handler.py`, `io.py`, `prompt_c2_static.txt`, `prompt_c3_bespoke.txt`

**Key points**
- `generate_interface_c2(context) -> (ClarificationData, CallLogRecord)`.
- `generate_interface_c3(context) -> (BespokeInterface{jsx, fields}, CallLogRecord)`.
- Prompts load at runtime; parse first-`{`-to-last-`}`, pydantic-validate; on failure a safe
  default + `parsed_ok=False` so the session proceeds.
- The C3 prompt's `{primitives}` block is injected from one source so prompt and host never
  drift — see [[C3 Primitives]].

**Connected**
- [[Conditions C1 C2 C3]] · [[Stub Call Layer]] · [[ambisql_static_interface]] §4 ·
  [[dynamic_interface]] §1 · [[model_prompts]] · renders in [[C2 Static Interface]] / [[C3 Dynamic Host]]
