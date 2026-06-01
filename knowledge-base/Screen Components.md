---
tags: [frontend]
---
# Screen Components

The per-screen React components the [[Wizard App]] renders, plus shared UI.

**Code:** [`frontend/src/components/`](../frontend/src/components)

**Screens**
- `ConsentDetails`, `Screening`, `StudyExplanation`
- `SchemaCard` (bland read-only schema), `QuestionAuthor` (question + intent, soft nudge)
- `LoadingScreen` (fixed-minimum delay, masks C3 latency)
- `PerceivedSuccess` (the two-stage confidence screens — see [[Overreliance Probe]])
- `ResultView` (rows + explanation + verbatim SQL)
- `SUS`, `AgencyItems`, `Debrief`
- `ui.jsx` — shared `Likert`, `RadioQuestion`, and the persistent `Footer` (contact + withdraw)

**Key points**
- All text comes from [[Copy]] keys. The two interface renderers live separately:
  [[C2 Static Interface]] and [[C3 Dynamic Host]].

**Connected**
- [[Wizard App]] · [[Copy]] · [[Logging]] (what each screen records via [[Main API]])
