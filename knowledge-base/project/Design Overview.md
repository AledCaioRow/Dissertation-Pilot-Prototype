---
tags: [project]
---
# Design Overview

One page on *why the study is built the way it is* — the experimental logic the code encodes.
For the "how to run it" side, see [[Local Launch]].

## The question
Does a **bespoke, model-generated interface (C3)** help people resolve ambiguous database
questions better — and with better-calibrated confidence — than a **fixed multiple-choice
clarifier (C2)**? C1 (model alone, no human) is the offline baseline.

## How the design isolates that
1. **Shared grounding.** Every condition sees the *same* schema card + question ([[Build Context]]);
   no extra hints layer. The only thing that varies is call 1's interface.
2. **One-shot, two calls.** Call 1 builds the interface; call 2 generates → executes → explains the
   SQL ([[One-shot Two-call Interaction]]). The explanation is post-execution, over real rows.
3. **Within-participant + counterbalanced.** Each participant does 2×C2 and 2×C3; order and
   question→condition mapping are balanced by id ([[Counterbalancing]]).
4. **Overreliance probe.** Two-stage confidence (before/after the result) + a deliberately
   under-specified question class surface confident-but-wrong answers ([[Overreliance Probe]]).
5. **Comparable cost.** Tokens/latency are logged per call so quality is weighed against cost.

## Conditions
- **C2** → fixed [[C2 Static Interface]] (multiple-choice only).
- **C3** → [[C3 Dynamic Host]] mounts generated JSX from the whitelisted [[C3 Primitives]].
- **C1** → [[Conditions C1 C2 C3|baseline]], offline, in the [[Analysis Notebook]].

**Connected:** [[The Experiment C2 vs C3]] · [[Ambiguity Classes]] · [[Backend Overview]] · [[Frontend Overview]] · [[Build Brief]]
