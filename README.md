# hitl-text-to-sql — a human-in-the-loop Text-to-SQL study apparatus

This repository is **two halves**. A **web application** (Python/FastAPI backend +
React/Vite frontend) runs the **live participant session**: it serves a step-through
wizard, generates and renders clarification interfaces, captures what the participant
clicks, executes SQL against real local SQLite databases, and logs everything to a
per-session JSON file. A separate **Jupyter notebook** (`analysis/analysis.ipynb`)
runs the **post-hoc analysis only**: it loads those logs, runs the no-human C1
baseline, scores answers against hand-written gold SQL, and produces the statistics
and exports. The live session is a web app — not a notebook — because the interfaces
are real JSX the participant clicks, and that input has to flow back to the backend,
which is impossible inside a Python kernel.

The study compares two clarification **conditions** for turning an ambiguous
natural-language question into SQL:

- **C2 (static)** — a faithful re-implementation of the AmbiSQL multiple-choice
  clarifier. Fixed layout, multiple-choice only. See `docs/spec/ambisql_static_interface.md`.
- **C3 (dynamic)** — a bespoke interface the model generates per question, free to
  choose a control matched to the shape of each ambiguity (slider, date-range,
  toggle, …). See `docs/spec/dynamic_interface.md`.

The single experimental variable is the **interface affordance**; everything else
(shared schema-card context, the same backend model, one-shot interaction) is held
constant by construction.

---

## Scope: the harness is built; the network call is stubbed

Everything here is real **except the Anthropic network call**. The prompts (in
editable `.txt` files), the I/O contracts, the React UI, the SQLite execution, the
counterbalancing and the logging are all real and run end to end. Every model call
goes through `backend/calls/_stub.py`, which returns a canned payload with the same
`.content` / `.usage` shape the real Messages API returns. The only thing left to do
to go live is flip `USE_STUB = False` in `backend/config.py` and provide an API key —
the call site is marked `# TODO: replace stub with real Anthropic call`.

---

## Repository layout

```
backend/        FastAPI session endpoints, organised by model call
  calls/        one folder per call: prompt .txt + io.py (pydantic) + handler.py (stubbed)
  conditions/   c1_baseline / c2_static / c3_bespoke orchestration
  context/      build_context.py — the shared schema-card + question block
  execution/    run_sql.py — REAL, tool-shaped SQLite execution
  schema/       load_schema.py + schema_card.py
  counterbalance/ assign.py — participant_id -> deterministic Assignment
  logging_io/   per-session JSON log + per-call log
frontend/       React 18 + Vite, plain JSX; the participant wizard
  src/content/copy.json   ALL participant-facing copy (one-file edit)
  src/components/         one component per screen + the two interfaces
analysis/       analysis.ipynb — post-hoc only
docs/           the canonical specs (hub + spokes); see below
bird_data/      NOT committed — drop the two BIRD .sqlite files here (see bird_data/README.md)
gold_sql/       gold-SQL scaffolding for scoring
session_logs/   per-session JSON written at runtime
```

### Documentation (hub + spokes)

`docs/CLAUDE_CODE_BRIEF.md` is the hub: architecture, structure, build order. The
spokes own the details and are meant to be tuned independently:

| Spoke | Governs |
|---|---|
| `docs/spec/ambisql_static_interface.md` | the C2 fixed interface (faithful AmbiSQL) |
| `docs/spec/dynamic_interface.md` | the C3 bespoke host + the component primitive set |
| `docs/prompts/model_prompts.md` | the three model-call prompts |
| `docs/content/page_copy.md` | every word the participant reads |

**Runtime loading.** Prompts load at runtime from `backend/calls/<call>/prompt*.txt`;
the frontend reads all copy from `frontend/src/content/copy.json`. The spoke `.md` is
the human-facing source of truth and initial content; keep the `.md` and the runtime
file in sync. A prompt or wording change is a one-file edit, no code change.

---

## Setup

### 1. Databases (one-time)

Drop the two BIRD SQLite files into `bird_data/` (not committed):

```
bird_data/california_schools/california_schools.sqlite
bird_data/financial/financial.sqlite
```

See `bird_data/README.md`. Paths are configured in `backend/config.py` (`DATABASES`).

### 2. Backend

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Sanity-check the databases and SQL execution without the frontend:

```bash
python -m backend.schema.load_schema      # prints each schema card
python -m backend.execution.run_sql       # runs a smoke query against each DB
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev        # Vite dev server, proxies /api -> http://localhost:8000
```

Open the printed URL and click through the wizard. With `USE_STUB = True` the whole
session works without an API key or the real databases populated (SQL execution will
report a neutral error if the `.sqlite` files are absent, which the wizard handles).

### 4. Analysis (after sessions are collected)

```bash
jupyter notebook analysis/analysis.ipynb
```

---

## Going live (later, by the researcher)

1. Set `USE_STUB = False` in `backend/config.py`.
2. Put a real key in `.env` (`ANTHROPIC_API_KEY=...`).
3. Replace the stub at the `# TODO: replace stub with real Anthropic call` site in
   `backend/calls/_stub.py` with a real `anthropic` Messages call. The stub already
   returns the same `.content[0].text` / `.usage` shape, so this is a one-spot change.
4. Confirm `MODEL_NAME` in `backend/config.py` (currently `claude-opus-4-7`; a newer
   Opus may have shipped — bump it if so).

---

## A note on showing the SQL

The participant is shown the generated SQL next to a confident, results-referencing
explanation — even though, by design, they know nothing about SQL. This is a
deliberate overreliance probe, not decoration: the overreliance literature predicts
showing the "evidence" they cannot verify *widens* the perceived-vs-actual gap. What
stays hidden is whether the answer is actually **correct** — that is scored post-hoc
by the researcher in the notebook, never shown in-session.
