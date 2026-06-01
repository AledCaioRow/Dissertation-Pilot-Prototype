---
tags: [frontend]
---
# Wizard App

The step-through state machine driving the whole session: one idea per screen, Back where
allowed, a persistent footer, incremental logging.

**Code:** [`frontend/src/App.jsx`](../../frontend/src/App.jsx)

## How it works (plain English)
1. On load it fetches `/config` and starts the session to get the [[Counterbalancing|assignment]].
2. `buildScreens(assignment)` produces the ordered screen list:
   **page 0 (mode)** → consent → details → study explanation → author the four questions →
   interaction block 1 → questionnaire → interaction block 2 → questionnaire → debrief.
3. Each interaction is: loading → interface → interface-confidence → (call 2 runs) → output →
   answer-confidence. Blocks are filtered by the condition order, so each question appears once.
4. Authoring is deferred to the authoring→interaction boundary, so the intent notes lock and Back
   works freely while authoring.
5. Page 0 stores the stub/live choice via `setMode`; the persistent footer (contact + withdraw)
   shows on every screen from the study-explanation screen onward.

**Connected:** [[API Client]] · [[Screen Components]] · [[C2 Static Interface]] · [[C3 Dynamic Host]] · [[Main API]] · [[Copy]] · [[Counterbalancing]]
