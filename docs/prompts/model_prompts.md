# Spoke: model prompts

> **PLACEHOLDER STATUS:** The prompt bodies in the runtime `.txt` files
> (`backend/calls/*/prompt*.txt`) have been stripped to clearly-labelled PLACEHOLDERs.
> Only the structural format strings (`{schema_card}`, `{question}`, etc.) and the
> output contracts remain. Fill in the instruction text in each `.txt` file before going
> live — the spec below is the design reference, not the actual prompt wording.

# Spoke: model prompts (spec reference)

Canonical spec and initial content for the model-call prompts. Each becomes a runtime-loaded `.txt` file under `backend/calls/<call>/`. Placeholders use `{name}` and are documented per prompt. Output-format and parsing rules are authoritative — match them in the corresponding `io.py`.

There are **three** prompts: C2 detection (call 1), C3 generation (call 1), and the shared query-generation-plus-explanation (call 2). There is no call 3.

These are **starting drafts**; the researcher iterates by editing the `.txt` files. The taxonomy in the C2 prompt must match `ambisql_static_interface.md` §3; the primitive list in the C3 prompt must match `dynamic_interface.md` §3.

Note on scope: the study exercises **four** ambiguity classes (schema-reference, value-reference, superlative-metric, temporal-window), all inside AmbiSQL's taxonomy. The C2 detection prompt still carries the **full** taxonomy (so C2 is a faithful, non-crippled AmbiSQL), but in practice only those four will arise from the authoring prompts.

---

## Shared context (built by `build_context.py`, injected into every call)

`{schema_card}` — the text schema (tables, columns, types, FKs) from `schema_card.py`. This carries everything the model needs to ground itself; there is no separate hints layer.
`{question}` — the participant's natural-language question.

All three calls below interpolate the same `{schema_card}`; only the instruction differs. This is what isolates the experimental variable.

---

## Call 1 — C2 static detection → `backend/calls/01_interface_generation/prompt_c2_static.txt`

Placeholders: `{schema_card}`, `{question}`.
Output: a single JSON object matching `ClarificationData` (see `ambisql_static_interface.md` §4). Parse: first `{` to matching last `}`, pydantic-validate.

```
You are a careful Text-to-SQL clarifier. Your job is to find genuine ambiguities in a
user's question — places where the question could map to more than one correct SQL — and
turn each into a single multiple-choice clarification a non-expert can answer.

Use ONLY this ambiguity taxonomy. Tag each ambiguity with exactly one type.

DB-related:
- unclear_schema_reference: not enough context to know which table/column to use for
  filtering, ranking, or aggregation (e.g. "oldest user" -> age or registration date).
- unclear_value_reference: a value that may not match what's stored, so the filter is
  unclear (e.g. "New York City" when the data stores "NYC").
- missing_sql_keywords: the intended operation is unstated (e.g. "users by date" -> sort,
  group, or filter?).
LLM-related:
- unclear_knowledge_source: unclear whether to read the database or infer (e.g. "female
  employees" -> a gender column, or inferred from names?).
- insufficient_reasoning_context: not enough information to reason (e.g. "current rate"
  without currencies or date).
- conflicting_knowledge: the question assumes something that contradicts the data.
- ambiguous_temporal_spatial_scope: a time or place constraint with multiple granularities
  (e.g. "after the 2018 World Cup" -> after the final, or after that year?).

Schema:
{schema_card}

Question:
{question}

Instructions:
- List only ambiguities that genuinely change the resulting SQL. Do not invent ambiguity.
- For each, write ONE multiple-choice question with 2-4 options. Every option needs a
  plain-language label and a short snippet grounded in the schema or its values (for a
  date, give the exact reference, e.g. "1975 (end year)" vs "1975-04-30 (end date)").
- Phrase questions and options so someone who knows nothing about SQL or databases can
  answer. No SQL terms, no column types in the labels.
- If there is no genuine ambiguity, return an empty "widgets" array.

Return ONLY this JSON object, no preamble:
{{"widgets": [{{"id": "amb_1", "ambiguity_type": "<one type above>", "title": "...",
"description": "...", "options": [{{"value": "...", "label": "...", "snippet": "..."}}]}}],
"allow_additional_constraints": true}}
```

(Note: literal braces in the example are doubled for `.format()`.)

---

## Call 1 — C3 bespoke interface → `backend/calls/01_interface_generation/prompt_c3_bespoke.txt`

Placeholders: `{schema_card}`, `{question}`, `{primitives}` (the primitive list from `dynamic_interface.md` §3, injected so the prompt and the host stay in sync).
Output: a single JSON object matching `BespokeInterface` (`dynamic_interface.md` §1). Parse: first `{` to matching last `}`, pydantic-validate; on JSX compile failure the host falls back (don't handle that here).

```
You design a small, clear interface that helps a non-expert pin down exactly what they
mean, so a correct SQL query can be written for their question. The user knows nothing
about SQL, databases, or schemas.

Schema:
{schema_card}

Question:
{question}

You may use ONLY these interface controls (no others):
{primitives}

Instructions:
- Find whatever ambiguities or missing details most affect getting the SQL right for THIS
  question against THIS schema. You are not limited to any fixed list of ambiguity types.
- For each, choose the control whose shape fits the choice: a slider or number input for a
  threshold or percentage; a date range for an unbounded time window; a toggle or radio for
  "all vs any" set logic; a column picker or radio for "which column"; checkboxes or
  multi-select for "which values".
- Use at most 6 controls. Order them most-important first.
- Every label and help text must be plain domain language the user can answer. Never use
  SQL terms, join types, or column data types in what the user reads.
- The component must call submitResponses({{...}}) exactly once, on its own submit button,
  passing an object keyed by each control's field id.

Return ONLY this JSON object, no preamble:
{{"jsx": "<a self-contained React component using only the controls above and calling
submitResponses(...)>", "fields": [{{"id": "f1", "label": "<plain-language label>"}}]}}
```

---

## Call 2 — query generation + post-execution explanation (shared by C2 and C3) → `backend/calls/02_query_generation/prompt.txt`

This is now a **two-step single call**: the model first returns the interpretation and SQL; `run_sql` executes it; the rows are fed back and the model returns the explanation referencing the actual result. There is no separate call 3. Implement either as a `run_sql` tool-call inside this completion, or as generate-sql → execute → explain folded into one handler.

Placeholders: `{schema_card}`, `{question}`, `{clarifications}` (labelled responses as `- <label>: <value>` lines), and — for the explanation step — `{rows_sample}` (first ~20 returned rows as readable text) and `{row_count}`.
Output: a single JSON object `{interpretation, sql, explanation}`. Parse: first `{` to matching last `}`, pydantic-validate.

```
You turn a user's question, plus their answers to clarification questions, into one correct
SQLite query, then explain the result plainly after it has been run.

Schema:
{schema_card}

Original question:
{question}

The user clarified:
{clarifications}

Step 1 — write the query:
- A single SQLite query that answers the question as clarified.
- Use ONLY what the user provided. Do not add filters they did not ask for.
- If something is still unresolved, make the most reasonable choice and say so honestly in
  the interpretation — do not pretend it was specified.

The query was run and returned {row_count} row(s). Sample:
{rows_sample}

Step 2 — explain, for someone who cannot read SQL: one short paragraph describing what the
result shows, in plain language, no SQL terms. Be straightforward; do not add caveats beyond
what the data supports.

Return ONLY this JSON object, no preamble:
{{"interpretation": "<one-line restatement of what the user means, after their
clarifications>", "sql": "<single SQLite query>", "explanation": "<one short plain-language
paragraph describing the actual result>"}}
```

`io.py`:

```python
class QueryGenerationResult(BaseModel):
    interpretation: str
    sql: str
    explanation: str
```

The participant is shown all three — `interpretation` (as framing), `sql` (verbatim), and `explanation` — on the output screen, alongside the result table.

---

## A note on showing the SQL, and your headline finding

The participant sees the generated SQL next to a confident, results-referencing explanation — even though they cannot read SQL. The overreliance literature predicts this *widens* the perceived-vs-actual gap (they are shown the "evidence" yet cannot verify it), so it is a theoretically motivated probe, not decoration.

**Future direction (not built):** a hidden *pre-execution* explanation (the model explains intent from the SQL alone, before running it) would let you compare pre- vs post-execution confidence. Noted in the report's future work.

---

## Related (knowledge base)
- [[Call 1 Interface Generation]] · [[Call 2 Query Generation]] · [[Stub Call Layer]]
- [[Overreliance Probe]] · [[Build Context]] · [[Home]]
