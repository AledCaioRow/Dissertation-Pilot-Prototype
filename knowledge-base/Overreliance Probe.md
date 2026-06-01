---
tags: [concept]
---
# Overreliance Probe

The participant is **shown the generated SQL** next to a confident, results-referencing
explanation — even though, by design, they can't read SQL. This is deliberate: the
overreliance literature predicts showing "evidence" they can't verify *widens* the
perceived-vs-actual gap. It's a theoretically motivated probe, not decoration.

**Key points**
- What stays hidden is **correctness** — no right/wrong marker in-session. Correctness is
  scored post-hoc — see [[Analysis Notebook]].
- Two-stage confidence: interface-confidence *before* the result, answer-confidence *after*
  — captured by [[Screen Components]] (PerceivedSuccess) and stored via [[Logging]].
- Rendered by ResultView — see [[Screen Components]] and [[page_copy]] (output copy).

**Connected**
- [[One-shot Two-call Interaction]] · [[Call 2 Query Generation]]
- [[model_prompts]] — "A note on showing the SQL"
