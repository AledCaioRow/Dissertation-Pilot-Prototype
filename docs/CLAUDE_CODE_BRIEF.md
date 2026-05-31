# Build brief (hub): text-to-SQL HITL study apparatus

This is the **hub** document. It owns the architecture, structure, and build order. Detailed specs meant to be tuned independently live in **spoke files** under `docs/`, listed in the document map below. Read this hub first, then read each spoke before building the part it governs.

Guiding rule: where this is silent or ambiguous, prefer the option that makes the project's structure more **obvious** and more **editable** over the option that is cleverer.

---

## 0. Document map (the spokes)

| Spoke | Governs | Edit it to change… |
|---|---|---|
| `docs/spec/ambisql_static_interface.md` | The C2 fixed interface (faithful AmbiSQL pattern) | how the static clarifier looks and behaves |
| `docs/spec/dynamic_interface.md` | The C3 bespoke interface host + the component primitive set | how generated interfaces are sandboxed; what controls C3 may use |
| `docs/prompts/model_prompts.md` | The three model-call prompts (C2 detect, C3 generate, shared query+explain) | what each call says to the model |
| `docs/content/page_copy.md` | All participant-facing copy + the four authoring prompts + questionnaire wording | every word the participant reads |

**Runtime loading (important for editability).** Prompts and participant copy are **loaded at runtime from editable files**, not hard-coded:
- Each model call reads its prompt from `backend/calls/<call>/prompt*.txt`. `docs/prompts/model_prompts.md` is the canonical spec and initial content.
- The frontend reads all copy from `frontend/src/content/copy.json`. `docs/content/page_copy.md` is the canonical spec and initial content.
- A prompt or wording change is then a one-file edit with no code change. Keep the spoke `.md` and the runtime file in sync; the `.md` is the human-facing source of truth.

---

## 1. Scope: build the harness, stub the API

You build the **harness and framework**, not the live model integration. Every Anthropic API call is a **stub** returning a canned payload matching the documented I/O contract, so the system runs end to end with no API key. You write the real **prompt text** (in files), the real **contracts**, the real **UI**, the real **SQL execution** (SQLite is local — make it real), and the real **logging**. The only thing left as `# TODO: replace stub with real Anthropic call` is the network call. The researcher flips `USE_STUB = False` later.

---

## 2. Two halves (state first in the README)

- A **web application** (Python backend + React frontend) runs the **live participant session**: serves the wizard pages, generates and renders interfaces, captures input, executes SQL, logs. It is a web app and not a notebook because the interfaces are real JSX the participant clicks and whose input flows back to the backend — impossible inside a Python kernel.
- A **Jupyter notebook** runs the **post-hoc analysis only**: load logs, run the C1 baseline, score against hand-written gold SQL, produce statistics and exports.

The README's first paragraph must make this split explicit.

---

## 3. The session, as a step-through wizard

A self-contained, **self-administered** wizard the participant completes **alone** (unmoderated, possibly remote): one idea per screen, a visible **Back** button throughout, plain language, deliberately bland styling (participants know nothing about SQL, databases, or schemas). Because nobody is in the room, every screen carries a persistent **"Questions? Contact {researcher}"** line and an **"Exit and withdraw"** control that ends the session cleanly (marks the log withdrawn, stops further screens). Full copy is in `docs/content/page_copy.md`. Phase order:

1. **Consent & details.** Participant ID, name + contact for consent records, consent checkboxes, plain-language data-use explanation.
2. **Study explanation.** What the study is and what they will do, plainly, no jargon.
3. **Authoring, per database (×2, counterbalanced order).** Each database screen: a plain explanation + a role-play framing ("imagine you are the schools-district officer…"), the schema shown blandly, then a task guiding them to ask a deliberately complex question (one needing a join plus one more advanced operation) while making clear the *intent* is theirs. Two questions per database (the two hosted ambiguity classes, surfaced naturally, never labelled "ambiguity"). Each: a question box and an **intent-note** box. Back button active.
   - All four questions + intent notes are authored here, **before any interface is seen** — the intent note is the contamination-free scoring anchor and must be locked pre-interaction.
4. **Interaction block 1 (condition by counterbalancing).** Per question: a **fixed loading screen** (masks C3's longer latency), then the generated interface, rendered **inside a bordered panel in the wizard** — for C3 the model's JSX is live-mounted in that panel (`C3DynamicHost`), for C2 the fixed component fills the same panel; the participant interacts and submits from inside it. On submit, SQL is generated, executed, and explained (call 2, post-execution), and the **output screen** appears showing the **result rows, the generated SQL, and the explanation together**. Confidence captured in two stages: interface-confidence *before* the output screen, answer-confidence *after*.
5. **Questionnaire (block 1's condition).** SUS (10) + four agency items + open-ended questions.
6. **Interaction block 2.** The other two questions through the other condition, same loading → interface-panel → output flow.
7. **Questionnaire (block 2's condition).**
8. **Debrief.** Overall preference + open-ended.

Everything from phase 1 onward logs to one per-session JSON file, written incrementally.

C1 (baseline, no human) is **not** in the session — run later in the analysis notebook against the four authored questions.

### Interaction model (one-shot, two calls)

"One-shot" = **one human turn**, not one API call. Behind a single submit:

- **Call 1** (differs by condition): C2 → detect ambiguities (the four-class AmbiSQL subset, see §3a) → clarification data for the fixed component (`ambisql_static_interface.md`). C3 → generate a query-specific interface + field manifest (`dynamic_interface.md`).
- *Human interacts, submits once.*
- SQL is generated and **executed** (real, local SQLite via `run_sql`), then **Call 2** produces the explanation *after* seeing the rows. Concretely: the model is given the question + labelled responses + shared context and returns `{interpretation, sql}`; `run_sql` executes the `sql`; the result rows are passed back into the same call's completion so it returns the `explanation` referencing the actual rows. Implement this as a single logical call that has the execution result available when it writes the explanation (a `run_sql` tool-call within call 2, or generate-sql → execute → explain folded into one handler). Either way it counts as **call 2** — there is no separate call 3.
- Participant sees, together on one screen: the **result rows**, the **generated SQL**, and the **plain-language explanation**.

C1 is one call (shared context → SQL) + execution; no human, no explanation needed for the participant (it's the offline baseline).

The participant is **shown the SQL** alongside the explanation. (This reverses the earlier hide-the-SQL stance — deliberately. Showing SQL + a confident explanation to a non-expert who cannot read SQL is a stronger overreliance probe, not a weaker one.)

The **shared context** (schema card + question) is built once by `backend/context/build_context.py` and reused; the only per-condition difference is the output instruction. The schema card carries the real tables, columns, types, and foreign keys, so no separate hint layer is needed. Enforce structurally — all conditions call the same builder — to isolate the experimental variable.

> **Future direction (not built):** a hidden *pre-execution* explanation call (the model explains its intent from the SQL alone, before running it) would let you compare pre- vs post-execution confidence. Noted in the report's future work; out of scope here.

---

## 4. Tech stack

**Backend:** Python 3.10+, FastAPI, uvicorn, pydantic v2, sqlite3 (stdlib), python-dotenv, tenacity (wire its retry around the stub now). `anthropic` is listed, imported only in the stubbed call layer.

**Frontend:** React 18 via Vite, **plain JavaScript/JSX** (not TypeScript). Rationale: C3 live-renders model-generated JSX via a sandbox (`react-live` or Babel-standalone + scoped mount); plain JS keeps that dynamic-eval path simple. One stylesheet, no CSS framework.

**Analysis:** Jupyter, pandas, scipy, optionally statsmodels.

Eventual real call: `claude-opus-4-7`, standard Messages API (response from `message.content[0].text`, usage from `message.usage`). The stub returns the same `.content`/`.usage` shape so going live is one line.

---

## 5. Directory structure (organised by call)

Each model call is its own folder (prompt file + I/O schema + stubbed handler), so the call structure is self-evident.

```
hitl-text-to-sql/
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
│
├── docs/                              # THE SPOKES
│   ├── spec/ambisql_static_interface.md
│   ├── spec/dynamic_interface.md
│   ├── prompts/model_prompts.md
│   └── content/page_copy.md
│
├── backend/
│   ├── main.py                        # FastAPI session endpoints (§6)
│   ├── config.py                      # ALL tunable parameters (§7)
│   ├── context/build_context.py       # the shared context block
│   ├── calls/
│   │   ├── _stub.py                    # shared mock; canned, correctly-shaped payloads
│   │   ├── 01_interface_generation/
│   │   │   ├── prompt_c2_static.txt    # runtime-loaded; content from model_prompts.md
│   │   │   ├── prompt_c3_bespoke.txt
│   │   │   ├── io.py
│   │   │   └── handler.py              # generate_interface_c2 / _c3  [STUBBED]
│   │   ├── 02_query_generation/
│   │   │   ├── prompt.txt               # call 2: post-execution; emits {interpretation, sql, explanation}
│   │   │   ├── io.py
│   │   │   └── handler.py              # generate_query (called AFTER run_sql; sees rows)  [STUBBED]
│   │   (no 03_result_summary — explanation is folded into call 2; see §3 interaction model)
│   ├── conditions/{c1_baseline,c2_static,c3_bespoke}.py
│   ├── execution/run_sql.py            # REAL sqlite execution + timeout (§8)
│   ├── schema/{load_schema,schema_card}.py
│   ├── counterbalance/assign.py        # participant_id → Assignment (§9)
│   └── logging_io/{session_log,call_log}.py
│
├── frontend/
│   ├── index.html ├── vite.config.js ├── package.json
│   └── src/
│       ├── main.jsx ├── App.jsx ├── api.js ├── styles.css
│       ├── content/copy.json           # ALL copy; content from page_copy.md
│       └── components/
│           ├── ConsentDetails.jsx ├── StudyExplanation.jsx
│           ├── SchemaCard.jsx ├── QuestionAuthor.jsx ├── LoadingScreen.jsx
│           ├── C2StaticInterface.jsx   # per ambisql_static_interface.md
│           ├── C3DynamicHost.jsx       # per dynamic_interface.md
│           ├── ResultView.jsx ├── PerceivedSuccess.jsx
│           ├── SUS.jsx ├── AgencyItems.jsx └── Debrief.jsx
│
├── analysis/analysis.ipynb             # post-hoc only (§10)
├── bird_data/                          # NOT committed; researcher populates
│   ├── california_schools/california_schools.sqlite
│   └── financial/financial.sqlite
├── session_logs/.gitkeep
└── gold_sql/{README.md,second_rater.csv}
```

`.gitignore`: `.env`, `bird_data/`, `session_logs/*.json`, `node_modules/`, `__pycache__/`, `.ipynb_checkpoints/`, `gold_sql/p*_t*.md`.

---

## 6. Backend endpoints (`backend/main.py`)

FastAPI, thin, delegating to `conditions/`. State keyed by `participant_id`, persisted on every write.

- `POST /session/start` `{participant_id}` → compute assignment, create log, return assignment.
- `POST /session/consent` → store consent + details.
- `POST /session/screening` → store screening answers.
- `GET  /schema/{name}` → schema as structured JSON for `SchemaCard`.
- `POST /author` → store one authored question + intent note as a stub trial.
- `POST /trial/interface` `{trial_id}` → run **call 1**; return clarification data (C2) or `{jsx, fields}` (C3). Log the call.
- `POST /trial/answer` `{trial_id, responses}` → generate SQL, run `run_sql`, then complete **call 2** with the rows to produce the explanation; return `{rows, column_names, sql, explanation}`. Log all calls' tokens/latency. **The SQL is returned and shown** (see §3).
- `POST /trial/perceived` → store two-stage ratings.
- `POST /questionnaire` `{condition, sus, agency, open_ended}` → store per-condition questionnaires.
- `POST /debrief` → store debrief + preference; mark complete.

Each endpoint validates with pydantic and appends to the log immediately.

---

## 7. `backend/config.py`

Primary tuning surface. Named constants + comments. At minimum:

```python
MODEL_NAME = "claude-opus-4-7"
MODEL_MAX_TOKENS_DEFAULT = 4096
MODEL_MAX_TOKENS_INTERFACE_GEN = 8192
MODEL_TEMPERATURE = 1.0
API_RETRY_ATTEMPTS = 3
API_RETRY_BACKOFF_SECONDS = 2

USE_STUB = True

BIRD_DATA_ROOT = "./bird_data"
DATABASES = {
    "california_schools": {"sqlite": "california_schools/california_schools.sqlite"},
    "financial":          {"sqlite": "financial/financial.sqlite"},
}
SCHEMA_CLASS_MAP = {
    "california_schools": ["schema_reference", "superlative_metric"],
    "financial":          ["value_reference", "temporal_window"],
}
# Four ambiguity classes across two databases = 4 questions/participant = 8 trials
# (4 questions x 2 participant-facing conditions). All four classes sit INSIDE AmbiSQL's
# detection taxonomy, so the C2-vs-C3 contrast is purely interface affordance, not detection.

SHOW_RESULT_ROW_LIMIT = 50
SQL_EXECUTION_TIMEOUT_SECONDS = 10
QUESTION_AUTHORING_MIN_CHARS = 15
LOADING_SCREEN_MIN_SECONDS = 2  # fixed loading screen always shows (masks C3's longer latency)

SESSION_LOG_DIR = "./session_logs"
LOG_PROMPTS_VERBATIM = True
PILOT_MODE = False
```

---

## 8. SQL execution (`backend/execution/run_sql.py`) — REAL, tool-shaped, feeds call 2

Local, not an API call. Implement for real, and structure it as a **standalone reusable function** so it can be registered as an Anthropic tool-use tool — because in this design it **is** used mid-call: call 2 generates SQL, `run_sql` executes it, and the returned rows are fed back so call 2 writes its explanation referencing the actual result (post-execution explanation). Build it tool-shaped so the model can invoke it within call 2 (or wire generate-sql → execute → explain as one handler).

`run_sql(db_name, sql) -> ExecutionResult` = `{success, rows, column_names, error, row_count}`. Read-only open, execute with timeout (thread + `join`), trim displayed rows to `SHOW_RESULT_ROW_LIMIT` but log true `row_count`. Empty result = success. Execution error → `success=False` + error string; the explanation step is told the query failed, and the frontend shows a neutral message but still collects the perceived items. `ResultView` displays the returned table **and the generated SQL** alongside the explanation.

---

## 9. Counterbalancing (`backend/counterbalance/assign.py`)

`assign(participant_id) -> Assignment`: `schema_order` (permutation of three), `condition_block_order` (`["C2","C3"]`/reverse), `slot_to_condition` (per schema, which hosted question → C2 vs C3, applied uniformly so exactly three C2 + three C3). 6×2×2 = 24 assignments; index by `participant_id % 24`. `describe(assignment)` for the start-of-session check; reproduce the 24-row table in `analysis.ipynb`.

> Implementation note (reconciling the brief): the configured study ships with **two**
> databases (`DATABASES` in §7), not three, so `assign.py` computes the counterbalance
> **data-driven from the configured databases** rather than hard-coding "permutation of
> three / 24". With two schemas it yields 2×2×2 = 8 balanced assignments
> (`participant_id % N`, N computed). Add a third database to `DATABASES` and the table
> grows to 24 with no code change. The §3 wizard runs each authored question once — two
> under C2 and two under C3 — so a participant sees 4 trials.

---

## 10. `analysis/analysis.ipynb` — post-hoc only

1. Load logs into pydantic objects.
2. Flatten to long `trials_df` + empty `actual_success`, `failure_attribution`, `false_confidence_flag`.
3. **C1 baseline:** run `c1_baseline.py` (stubbed) per authored question; append `condition="C1"` rows.
4. **Gold scaffold:** per question write `gold_sql/p{NN}_t{NN}.md`; `score_trial(...)` writes `actual_success ∈ {correct,partial,incorrect}`, sets `false_confidence_flag`, records failure-attribution; `cohens_kappa()` from `second_rater.csv`.
5. **Descriptives:** success by condition + class; perceived-vs-actual gap by condition + class; the **2×2 reliance matrix** per condition (overreliance / underreliance / appropriate); failure-attribution distribution.
6. **Calibration:** confidence vs correctness.
7. **SUS + agency:** per-condition means + bootstrapped CIs.
8. **Cost:** mean/SD tokens + latency per condition; C3 compile-success rate.
9. **Secondary model (optional):** mixed-effects logistic, labelled effect-size estimation.
10. **Qual export:** open-text + per-trial question-vs-output table to CSV.

Do not automate scoring or thematic analysis.

---

## 11. Edge cases

Invalid JSON → surface raw, mark error trial, allow re-run/skip. SQL with prose → first ```sql block else first `SELECT|WITH`. Empty C2 widgets → skip interaction, straight to call 2, log it. C3 won't compile → manifest text-input fallback, `compile_success=false`, don't abort. Execution error/empty → §8. Crash → resume from last logged phase.

---

## 12. Out of scope

Real network call (TODO only); automated scoring/thematic analysis; batch orchestration; AI self-verification; probe/catch trials; unanswerability detection; auth/deploy/containers.

---

## 13. Build order

(1) config/env/req/README skeleton → (2) `schema/` + sanity script → (3) `run_sql.py` real + test → (4) `_stub.py` + three call folders → (5) `build_context.py` → (6) `conditions/` (c1,c2,c3) → (7) `counterbalance/` → (8) `logging_io/` round-trip → (9) `main.py`, verify full session via HTTP against stub → (10) `frontend/` per `page_copy.md` + interface spokes, verify wizard click-through → (11) `analysis.ipynb` cells 1–5. Runnable at each checkpoint.

---

## 14. Style

Type-hint Python; pydantic at boundaries; short functions; informative server logs. British English in participant-facing text. The C3 primitive set lives in **one** source of truth (`dynamic_interface.md`), referenced by both the host scope and the C3 prompt.

---

## 15. Confirm only these

1. `claude-opus-4-7` (confirm if newer Opus shipped). 2. The two BIRD `.sqlite` files (`california_schools`, `financial`) placed at configured paths. 3. Any demographics beyond age band + SQL/DB experience. Otherwise: build, reading each spoke before its part.
