---
tags: [frontend]
---
# C2 Static Interface

The faithful AmbiSQL clarifier whose structure is **constant** across every question:
a stacked list of clarification cards (radio groups + DB snippets) plus one optional
free-text "additional constraints" box, then Submit.

**Code:** [`frontend/src/components/C2StaticInterface.jsx`](../frontend/src/components/C2StaticInterface.jsx)

**Key points**
- Multiple-choice **only** — never a slider/date/toggle. That affordance limit *is* the
  experiment ([[The Experiment C2 vs C3]]).
- Receives `ClarificationData` from [[Call 1 Interface Generation]]; emits the shared responses
  contract on submit → [[Call 2 Query Generation]].
- Empty widgets → skip note + proceed.

**Connected**
- [[ambisql_static_interface]] (spec) · [[C3 Dynamic Host]] (the contrast) · [[Wizard App]]
