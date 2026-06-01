---
tags: [analysis]
---
# Analysis Notebook

The post-hoc half. Loads the session logs, runs the C1 baseline, scores against hand-written
gold SQL, and produces the statistics. Scoring and thematic analysis are **not** automated.

**Code:** [`analysis/analysis.ipynb`](../analysis/analysis.ipynb) · gold workflow [`gold_sql/README.md`](../gold_sql/README.md)

**Cells**
1. Load logs ([[Logging]]) into pydantic. 2. Flatten to `trials_df` + empty hand-scored cols.
3. **C1 baseline** ([[Conditions C1 C2 C3]]) per authored question. 4. Gold scaffold +
`score_trial` + `cohens_kappa`. 5. Descriptives: success by condition+class, perceived-vs-actual
gap, the 2×2 reliance matrix, failure attribution. Plus SUS/cost/qual export and the
[[Counterbalancing]] table.

**Key points**
- The reliance matrix and false-confidence flag operationalise the [[Overreliance Probe]].

**Connected**
- [[Logging]] · [[Conditions C1 C2 C3]] · [[Counterbalancing]] · [[Ambiguity Classes]] · [[CLAUDE_CODE_BRIEF]] §10
