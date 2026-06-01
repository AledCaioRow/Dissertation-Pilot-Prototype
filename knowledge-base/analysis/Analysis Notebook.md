---
tags: [analysis]
---
# Analysis Notebook

The post-hoc analysis: loads the per-participant session logs and computes the C2-vs-C3 (and
model-alone C1) comparisons.

**Code:** [`analysis/analysis.ipynb`](../../analysis/analysis.ipynb)

## How it works (plain English)
1. It reads every `session_logs/p*.json` into one tidy, trial-level table.
2. It joins each trial to its condition via the [[Counterbalancing|assignment]].
3. It derives the headline measures per condition: task success, **overreliance** (confident +
   wrong), the confidence shift before→after the result, and the cost side (tokens, latency,
   C3 compile-success rate).
4. It runs the **C1 baseline** offline ([[Conditions C1 C2 C3|run_baseline]]) to get the
   model-alone reference, then compares C1 vs C2 vs C3.
5. It outputs the comparison tables/plots for the write-up.

**Connected:** [[Logging]] (input) · [[Overreliance Probe]] · [[The Experiment C2 vs C3]] · [[Counterbalancing]]
