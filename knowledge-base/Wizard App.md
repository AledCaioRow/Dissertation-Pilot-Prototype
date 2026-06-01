---
tags: [frontend]
---
# Wizard App

The step-through state machine driving the whole session: one idea per screen, Back where
allowed, persistent footer, incremental logging.

**Code:** [`frontend/src/App.jsx`](../frontend/src/App.jsx)

**Flow** (built from the [[Counterbalancing|assignment]])
consent → details → study explanation → **author four questions** (locked pre-interaction) →
interaction block 1 → questionnaire → interaction block 2 → questionnaire → debrief.
Each interaction: loading → interface → interface-confidence → (call 2 runs) → output → answer-confidence.

**Key points**
- `buildScreens(assignment)` produces the ordered screen list; blocks filtered by condition order.
- Authoring is deferred to the authoring→interaction boundary (`ensureTrials`) so intent locks
  and Back works freely during authoring.
- Detects backend at startup (`detectMode`) → real or mock; shows a demo banner in mock.

**Connected**
- [[API Client and Mock]] · [[Screen Components]] · [[C2 Static Interface]] · [[C3 Dynamic Host]]
- [[Main API]] (endpoints it calls) · [[Copy]] · [[Counterbalancing]]
