---
tags: [frontend]
---
# Screen Components

The individual wizard screens and small shared pieces that [[Wizard App]] composes — one file per
step, each reading its text from [[Copy]].

**Code:** [`frontend/src/components/`](../../frontend/src/components)

## How it works (plain English)
1. `ModeSelect` is **page 0** (researcher set-up): pick stubbed vs live, then `setMode` + continue.
2. Consent/screening/study-explanation screens gate entry and capture consent + eligibility.
3. `Authoring` collects each free-text question (+ intent note) with a minimum-length guard.
4. `SchemaView` shows the bland schema card; `LoadingScreen` enforces a minimum dwell so timing is
   comparable across conditions.
5. `ConfidenceGate` captures the two-stage confidence (before result, after result).
6. `ResultView` shows the answer **with the SQL and the explanation**; questionnaire/debrief close out.
7. `Footer` (contact + withdraw) renders from the study-explanation screen onward.

**Connected:** [[Wizard App]] · [[Copy]] · [[C2 Static Interface]] · [[C3 Dynamic Host]] · [[Overreliance Probe]] (confidence) · [[Page Copy]]
