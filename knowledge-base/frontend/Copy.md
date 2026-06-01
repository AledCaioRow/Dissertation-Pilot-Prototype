---
tags: [frontend]
---
# Copy

All participant-facing (and page-0 operator) text in one JSON file, so wording can be reviewed
and edited without touching component code.

**Code:** [`frontend/src/content/copy.json`](../../frontend/src/content/copy.json)

## How it works (plain English)
1. One JSON object keyed by screen/section: `mode` (page 0), `consent`, `screening`, `study`,
   `author`, `confidence`, `questionnaire`, `debrief`, plus shared `nav` and `footer`.
2. Components import the JSON and read their block by key — no copy is hard-coded in JSX.
3. Neutral, non-leading wording throughout: no "AI", no praise, no think-aloud/moderator script.
4. The one field to fill before a real run is `footer.contact` (researcher name / email).

**Key points**
- The `mode` block is operator-facing, so it may mention the API/stub plainly; everything else is
  participant-facing and stays neutral.

**Connected:** [[Page Copy]] (spec) · [[Wizard App]] · [[Screen Components]] · [[Overreliance Probe]]
