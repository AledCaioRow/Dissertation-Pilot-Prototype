# Spoke: C2 — the AmbiSQL static interface

Governs the **C2** condition: a fixed, taxonomy-driven clarification interface that is a faithful re-implementation of the AmbiSQL interaction pattern (Ding, Lin & Zeng, 2025, *AmbiSQL: Interactive Ambiguity Detection and Resolution for Text-to-SQL*, arXiv:2508.15276), adapted to this study's one-shot design and single shared backend.

This file is the source of truth for: the detection taxonomy C2 uses, the clarification-data contract call 1 emits, and the fixed React component that renders it. The C2 detection prompt in `model_prompts.md` must match the taxonomy here.

---

## 1. Why C2 must be faithful, and what is deliberately fixed

C2 is the comparison baseline for C3. For the comparison to be fair, C2 must be a **genuine** AmbiSQL, not a weakened one — otherwise any C3 advantage is an artefact of crippling C2. So C2 implements AmbiSQL's **full** taxonomy (both branches, below) and its multiple-choice clarification pattern as described in the paper.

The single defining constraint — and the experimental point — is that **C2 only ever renders multiple-choice questions** (plus one optional free-text "additional constraints" box, which AmbiSQL also has). Even when C2 correctly detects an ambiguity whose natural resolution would be a slider (a threshold), a date-range picker (a temporal window), or a toggle (set logic), it must still present it as multiple-choice options. This is true to AmbiSQL (the paper renders all clarifications as dropdown multiple-choice, stating MCQs "reduce answer uncertainty compared with free-text answers") and it is exactly the affordance limitation that C3 is being tested against. **Do not make C2 adaptive. Do not let C2 emit any non-MCQ control.**

---

## 2. Deliberate differences from the AmbiSQL paper

Document these in code comments so the fidelity is auditable:

- **One-shot, not iterative.** The paper's Stage 2 re-runs ambiguity detection after the user clarifies, to catch newly-introduced ambiguity, looping until none remain. **We do not loop.** Detection runs once (call 1); the user answers once; we proceed to query generation (call 2). The re-detection loop is out of scope for this study.
- **Single backend.** The paper feeds its rewritten query to a separate downstream Text-to-SQL system (XiYan-SQL). Here, both detection (call 1) and SQL generation (call 2) run on the same model (Opus), so the only variable between C2 and C3 is the interface.
- **Our own renderer.** We render in a fixed React component, not the paper's web app, but we reproduce its layout (a stacked list of clarification cards, each with a question, a description, multiple-choice options carrying database snippets, plus an optional additional-constraints field).
- **No "Compare against ground truth" button.** The paper's demo has one; we do not show correctness to the participant (it would contaminate perceived success). Scoring is done post-hoc by the researcher.

---

## 3. The detection taxonomy (full AmbiSQL taxonomy — used verbatim by the C2 detection prompt)

C2 detection carries the **full** taxonomy below so it is a faithful, non-crippled AmbiSQL. Note, however, that this study's authoring prompts only ever elicit **four** of these classes — `unclear_schema_reference` (covering superlative/metric), `unclear_value_reference`, `missing_sql_keywords` is *not* targeted, and `ambiguous_temporal_spatial_scope` (the temporal window). The four exercised classes are: schema-reference, superlative-metric (a form of schema-reference), value-reference, and temporal-window. All four sit inside the taxonomy, so C2 can genuinely detect every ambiguity the study presents — which is the point: the C2-vs-C3 contrast is then *purely* about interface affordance (multiple-choice vs a fitted control), with no detection-coverage confound.

Two dimensions, seven subcategories. Each detected ambiguity is tagged with one subcategory (logged as `ambiguity_type`).

**DB-related ambiguity** — unclear/underspecified references to schema or content:
- `unclear_schema_reference` — not enough context to know which table/column to use for filtering, ranking, or aggregation (paper's example: "oldest user" → age or registration date). *Note: superlative/metric ambiguity lives here.*
- `unclear_value_reference` — a value that does not match stored values, so the WHERE condition is unclear (e.g. "New York City" when the DB stores "NYC").
- `missing_sql_keywords` — the intended operation is unstated (e.g. "users by registration date" → ORDER BY vs GROUP BY vs WHERE).

**LLM-related ambiguity** — misuse of model reasoning beyond DB content:
- `unclear_knowledge_source` — unclear whether to read the DB or infer (e.g. "female employees" → a gender column vs inference from names).
- `insufficient_reasoning_context` — not enough information to reason (e.g. "current exchange rate" without target currencies or date).
- `conflicting_knowledge` — assumptions in the question contradict facts or DB contents.
- `ambiguous_temporal_spatial_scope` — temporal/spatial constraints underspecified at multiple granularities (paper's example: "after the 2018 World Cup" → after the final or after the tournament year). *Note: this means C2 DOES detect temporal-window ambiguity — it just can only offer MCQ options for it.*

The detection prompt includes, for each subcategory, the definition plus one short example, following the paper's in-context-learning approach (definition + concise taxonomy + representative examples).

---

## 4. Clarification-data contract (call 1, C2 output)

Call 1 (C2) returns **only** this JSON object. `parse_widget_spec` strips preamble (first `{` to matching last `}`) and validates with pydantic.

```json
{
  "widgets": [
    {
      "id": "amb_1",
      "ambiguity_type": "unclear_schema_reference",
      "title": "Which figure do you mean by \"top-performing\" school?",
      "description": "The data has several score columns; 'top' could rank by any of them.",
      "options": [
        {"value": "avg_math",   "label": "Highest average maths score",    "snippet": "satscores.AvgScrMath — average maths SAT score per school"},
        {"value": "avg_total",  "label": "Highest combined SAT score",      "snippet": "AvgScrMath + AvgScrRead + AvgScrWrite"},
        {"value": "num_takers", "label": "Most students who sat the SAT",   "snippet": "satscores.NumTstTakr — number of test takers"}
      ]
    }
  ],
  "allow_additional_constraints": true
}
```

Rules:
- One widget per detected ambiguity. 2–4 options each.
- Every option carries a plain-language `label` and a database-grounded `snippet` (the paper attaches a relevant DB snippet to each schema/value option, and an exact reference to each temporal option — e.g. "1975 (end year)" vs "1975-04-30 (end date)").
- `ambiguity_type` is one of the seven subcategories in §3 (for logging which types fire).
- If no ambiguity is detected, return `"widgets": []` (the session then skips the interaction and passes the original question to call 2 — log the skip).
- `allow_additional_constraints` defaults `true`.

pydantic (`backend/calls/01_interface_generation/io.py`):

```python
class C2Option(BaseModel):
    value: str
    label: str
    snippet: str | None = None

class C2Widget(BaseModel):
    id: str
    ambiguity_type: Literal[
        "unclear_schema_reference","unclear_value_reference","missing_sql_keywords",
        "unclear_knowledge_source","insufficient_reasoning_context",
        "conflicting_knowledge","ambiguous_temporal_spatial_scope"]
    title: str
    description: str | None = None
    options: list[C2Option]

class ClarificationData(BaseModel):   # the C2 call-1 output
    widgets: list[C2Widget]
    allow_additional_constraints: bool = True
```

---

## 5. The fixed component (`frontend/src/components/C2StaticInterface.jsx`)

A hand-written React component whose **structure is constant** across every question. It receives `ClarificationData` and renders, in order:

1. A short standing instruction (from `copy.json`, e.g. "Answer these questions to help the system understand exactly what you mean.").
2. A **stacked list of clarification cards**, one per widget, each card showing:
   - the `title` in bold;
   - the `description` in smaller grey text beneath;
   - the `options` as a **radio group** (or a dropdown — pick one and keep it constant; radio is more legible for non-experts), each option showing its `label` with the `snippet` in small grey text under it.
3. If `allow_additional_constraints`, an **"Anything else to add?" free-text box** (this is AmbiSQL's additional-constraints field — a place for the participant to add a constraint the multiple-choice options did not cover, e.g. "only members who joined this year").
4. A single **Submit** button, disabled until every radio group has a selection (the free-text box is optional).

Layout mimics the AmbiSQL ambiguity-resolution panel: a clean vertical stack of cards. Styling deliberately bland. British English throughout.

On submit, produce the shared responses contract (see `dynamic_interface.md` §contract — both interfaces use the same shape):

```json
{ "trial_id": "...",
  "responses": [
    {"field_id": "amb_1", "label": "Which figure do you mean by 'top-performing' school?", "value": "avg_total"},
    {"field_id": "additional_constraints", "label": "Anything else to add?", "value": "only schools in Los Angeles County"}
  ] }
```

Include `additional_constraints` in `responses` only if the participant typed something. The `label` is what lets call 2 and the logs interpret each response.

---

## 6. Worked example (grounded in this study's schemas)

For a `california_schools` superlative question — *"Which is the top-performing school in Los Angeles?"* — C2 detection should yield roughly:

- Widget 1, `unclear_schema_reference`: "Which figure do you mean by 'top-performing'?" → options: highest average maths / highest combined SAT / most test takers, each with its column snippet.
- Widget 2, `unclear_value_reference`: "How should we match 'Los Angeles'?" → options: county = "Los Angeles" / city = "Los Angeles", each with a snippet of the stored values.
- `allow_additional_constraints: true`.

This is the entire C2 interaction: two multiple-choice cards plus an optional text box. Note that even where a date or threshold is at issue (in other schemas), C2 must still express it as multiple-choice — that constraint is the experiment.

---

## 7. What C2 must never do

- Never render a slider, number input, date picker, date-range, toggle, multi-select beyond radio, schema/column clicker, or any generated/bespoke control. Multiple-choice (+ the one optional free-text box) only.
- Never change its layout per question.
- Never show **correctness** to the participant (no "Compare against ground truth", no right/wrong marker). The generated SQL itself **is** shown on the output screen (alongside the explanation) — that is intended (a non-expert seeing SQL they cannot read next to a confident explanation is the overreliance probe). What stays hidden is whether the answer is *correct*.
- Never loop / re-detect after the participant answers.

---

## 8. Logging (for the analysis)

From C2 trials, the log must capture: which `ambiguity_type`s fired, the full options shown per widget, the participant's chosen `value` per widget, and the `additional_constraints` text. This feeds the per-class analysis and lets you compare, for the same ambiguity class, how C2's multiple-choice resolution fared against C3's bespoke control.
