# Gold SQL — manual scoring

Scoring is **deliberately manual** (build brief §10, §12 — no automated scoring). The
analysis notebook writes one scaffold file per trial here, named:

```
gold_sql/p{NN}_{trial_id}.md      e.g. gold_sql/p07_p7_t3.md
```

These per-trial files are **git-ignored** (`gold_sql/p*_t*.md`) so participant-derived
content stays out of version control.

## Workflow

1. Run cells 1–4 of `analysis/analysis.ipynb`. Cell 4 writes a scaffold per trial,
   pre-filled with the question, the locked intent note (the contamination-free scoring
   anchor), and the SQL the system generated.
2. For each file, write the **gold SQL** and a rating: `correct` | `partial` | `incorrect`,
   plus a failure attribution if it went wrong.
3. Back in the notebook, call `score_trial(all_df, trial_id, 'correct', ...)` to record
   each rating. This also sets the `false_confidence_flag` (the participant was confident
   but the answer was not correct — the overreliance signal).

## Second rater

`second_rater.csv` is a template for an independent rater. Fill `actual_success` for a
subset (or all) trials; `cohens_kappa()` in the notebook computes inter-rater agreement.
Columns: `trial_id,actual_success` (`actual_success` ∈ {correct, partial, incorrect}).
