---
tags: [concept]
---
# Stub vs Live

The harness is fully built; only the **Anthropic network call is stubbed**. In stub mode every
model call returns a canned payload shaped exactly like the real Messages response, so the
whole study runs end to end with **no API key**.

**Choosing the mode** — two ways, with the runtime choice winning:
- **Page 0 of the wizard** (researcher set-up) picks *Stubbed* or *Live API* per session; the
  backend stores it on the session and threads it through every model call — see [[Wizard App]]
  and [[Main API]] (`/session/mode`).
- The default the selector starts on comes from `USE_STUB` in `backend/.env` — see [[Config]].

**Key points**
- The one place that changes to go live is marked `# TODO: replace stub with real Anthropic
  call` — see [[Stub Call Layer]]. Until it is implemented, *Live* errors and *Stub* is the default.
- The Anthropic key lives only in `backend/.env` on the laptop — it never reaches the browser.
- SQL execution is **real** even while stubbed — see [[Run SQL]].

**Connected**
- [[Backend Overview]] · [[Call 1 Interface Generation]] · [[Call 2 Query Generation]]
- [[Local Launch]] · [[Build Brief]] §1 (scope), §4 (eventual real call)
