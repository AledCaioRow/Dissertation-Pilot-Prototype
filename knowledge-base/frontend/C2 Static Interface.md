---
tags: [frontend]
---
# C2 Static Interface

The faithful AmbiSQL clarifier whose structure is **constant** across every question: a stacked
list of clarification cards (radio groups + DB snippets) plus one optional free-text box, then Submit.

**Code:** [`frontend/src/components/C2StaticInterface.jsx`](../../frontend/src/components/C2StaticInterface.jsx)

## How it works (plain English)
1. It receives `ClarificationData` (the widgets) from [[Call 1 Interface Generation]].
2. It renders one card per widget: a bold question, a grey description, and a **radio group** whose
   options each show a label + a small database snippet.
3. If allowed, it shows a single optional "Anything else to add?" text box.
4. Submit is disabled until every radio group has a selection; on submit it emits the shared
   responses contract (`{field_id, label, value}` per widget, plus the text box if filled).
5. Multiple-choice **only** — never a slider/date/toggle. That affordance limit *is* the experiment.

**Connected:** [[AmbiSQL Static Interface]] (spec) · [[C3 Dynamic Host]] (the contrast) · [[Wizard App]] · [[The Experiment C2 vs C3]]
