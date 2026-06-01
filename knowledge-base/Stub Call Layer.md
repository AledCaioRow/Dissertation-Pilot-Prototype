---
tags: [backend]
---
# Stub Call Layer

The single entry point every handler uses for a model completion. While stubbed it returns
canned, correctly-shaped payloads (`.content[0].text`, `.usage`); the one branch that changes
to go live is marked `# TODO: replace stub with real Anthropic call`.

**Code:** [`backend/calls/_stub.py`](../backend/calls/_stub.py)

**Key points**
- `complete(kind=…, prompt=…, …)` wrapped in tenacity retry; `kind` selects the canned payload.
- Canned payloads per call: C2 widgets, C3 JSX (`Interface` component using [[C3 Primitives]]),
  query SQL (table-free so it executes anywhere), explanation, C1 baseline.
- Same shape stubbed or live → going live is genuinely one spot. See [[Stub vs Live]].

**Connected**
- [[Call 1 Interface Generation]] · [[Call 2 Query Generation]] · [[Conditions C1 C2 C3]] · [[Config]]
