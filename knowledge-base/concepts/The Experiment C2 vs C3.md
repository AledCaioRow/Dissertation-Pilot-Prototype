---
tags: [concept]
---
# The Experiment — C2 vs C3

The study compares two ways of clarifying an ambiguous natural-language question before it
becomes SQL. The **single variable under test is the interface affordance** — everything
else (shared context, same backend model, one human turn) is held constant by construction.

**Key points**
- **C2 (static):** a faithful re-implementation of AmbiSQL — multiple-choice clarifications
  only, fixed layout. See [[C2 Static Interface]] and [[AmbiSQL Static Interface]].
- **C3 (dynamic):** the model generates a bespoke interface per question, free to pick a
  control matched to the ambiguity (slider, date-range, toggle…). See [[C3 Dynamic Host]],
  [[C3 Primitives]] and [[Dynamic Interface]].
- Fairness: C2 carries the **full** AmbiSQL taxonomy so any C3 win isn't from crippling C2.
- [[Counterbalancing]] assigns two questions to C2 and two to C3 per participant.

**Connected**
- [[One-shot Two-call Interaction]] — what happens behind one submit
- [[Ambiguity Classes]] — the four classes both conditions face
- [[Overreliance Probe]] — why the SQL is shown to non-experts
- [[Build Brief]] — §3 the session, §3a the conditions
