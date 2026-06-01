---
tags: [concept]
---
# Stub vs Live

The harness is fully built; only the **Anthropic network call is stubbed**. With
`USE_STUB = True` every model call returns a canned payload shaped exactly like the real
Messages response, so the system runs end to end with no API key.

**Key points**
- The switch and all tunables live in [[Config]].
- The one place that changes to go live is marked `# TODO: replace stub with real Anthropic
  call` — see [[Stub Call Layer]].
- SQL execution is **real** even while stubbed — see [[Run SQL]].
- The frontend has its own standalone fallback (mock) for running with no backend at all —
  see [[API Client and Mock]] and [[Prototype Deployment]].

**Connected**
- [[Backend Overview]] · [[Call 1 Interface Generation]] · [[Call 2 Query Generation]]
- [[CLAUDE_CODE_BRIEF]] §1 (scope), §4 (eventual real call)
