# hitl-text-to-sql — a human-in-the-loop Text-to-SQL study apparatus

## How to run the study app

This is a **local, supervised study** — the backend and frontend run together on your machine;
there is no hosted/online version. One step:

- **Windows:** double-click **`start.bat`** (or run `./start.ps1`).
- **Mac/Linux:** run **`./start.sh`**.

The first run installs dependencies; then the backend starts on `http://localhost:8000`, the
frontend on `http://localhost:5173`, and your browser opens automatically.

It runs in **stub mode out of the box (no API key needed)** — you can click the entire wizard,
including the **C3** dynamic interface. **Page 0** lets you choose *Stubbed* or *Live API* per
session.

**Manual fallback** (two terminals): `python -m uvicorn backend.main:app --port 8000`, and
`npm --prefix frontend run dev`.

**To go live:** copy `backend/.env.example` → `backend/.env`, set `USE_STUB=False` and
`ANTHROPIC_API_KEY=…` (see *Going live* below). The key stays in the backend, never the browser.

📓 **Design knowledge base:** open the [`knowledge-base/`](knowledge-base/) folder as an
[Obsidian](https://obsidian.md) vault and start at
[`knowledge-base/README.md`](knowledge-base/README.md) — the notes are wiki-linked into a
connection graph spanning the concepts, the code and the specs.

---

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

## Content status — all invented text is stripped; placeholders throughout

All fabricated/invented content has been removed and replaced with clearly-labelled
`PLACEHOLDER` strings. Nothing in the wizard shows convincing fake text. The following
need to be filled in before running participants:

| What | Where | Key(s) |
|---|---|---|
| Consent text + 4 checkboxes | `frontend/src/content/copy.json` | `consent.body`, `consent.checkboxes` |
| Study explanation | `frontend/src/content/copy.json` | `study_explanation.body` |
| Database intro copy (×2) | `frontend/src/content/copy.json` | `db_intro.california_schools.body`, `db_intro.financial.body` |
| Authoring prompts + intent nudges (×4) | `frontend/src/content/copy.json` | `authoring.california_schools:schema_reference`, `authoring.california_schools:superlative_metric`, `authoring.financial:value_reference`, `authoring.financial:temporal_window` — `.task` and `.then` sub-keys each |
| Loading body text | `frontend/src/content/copy.json` | `loading.body` |
| Interface standing instruction + skip note | `frontend/src/content/copy.json` | `interface.standing_instruction`, `interface.skip_note` |
| Output body + error + empty messages | `frontend/src/content/copy.json` | `output.body`, `output.error`, `output.empty` |
| Interface + answer confidence questions | `frontend/src/content/copy.json` | `interface_confidence.question`, `answer_confidence.wanted_question`, `answer_confidence.confidence_question` |
| Questionnaire heading + SUS intro + 10 SUS items | `frontend/src/content/copy.json` | `questionnaire.heading`, `questionnaire.sus_intro`, `questionnaire.sus_items` (array of 10) |
| 4 agency items + intro | `frontend/src/content/copy.json` | `questionnaire.agency_intro`, `questionnaire.agency_items` |
| 3 open-ended items + intro | `frontend/src/content/copy.json` | `questionnaire.open_intro`, `questionnaire.open_items` |
| 3 debrief open items + closing text | `frontend/src/content/copy.json` | `debrief.open_items`, `debrief.final` |
| C2 prompt body | `backend/calls/01_interface_generation/prompt_c2_static.txt` | Replace the `[PLACEHOLDER…]` block |
| C3 prompt body | `backend/calls/01_interface_generation/prompt_c3_bespoke.txt` | Replace the `[PLACEHOLDER…]` block |
| Query + explanation prompt body | `backend/calls/02_query_generation/prompt.txt` | Replace the `[PLACEHOLDER…]` block |

The C2 and C3 interface stubs (in stub mode) now render a plainly-labelled grey
PLACEHOLDER box rather than any mock content.

---

## Dev skip flags — bypass wizard phases for testing

To skip wizard phases without going through every screen, open
`frontend/src/App.jsx` and change line:

```js
const SKIP_ALL = false;
```
to:
```js
const SKIP_ALL = true;
```

This makes a yellow **"DEV: skip →"** button appear at the top of every phase.
Click it to jump past that screen without filling in any data. Individual phases
can also be toggled in `SKIP_CONFIG` below `SKIP_ALL`.

The **loading screen** skip is handled specially — it synthesises placeholder
interface data (placeholder flag, no JSX) so downstream screens (interface, output)
render their own PLACEHOLDER boxes rather than crashing.

**Default is `SKIP_ALL = false`** — change it back before running participants.

---

## Scope: the harness is built; the network call is stubbed

Everything here is real **except the Anthropic network call**. The prompts (in
editable `.txt` files), the I/O contracts, the React UI, the SQLite execution, the
counterbalancing and the logging are all real and run end to end. Every model call
goes through `backend/calls/_stub.py`, which returns a canned payload with the same
`.content` / `.usage` shape the real Messages API returns. Stub-vs-live is chosen
**per session on page 0** (the default coming from `USE_STUB` in `backend/.env`); the
only thing left to do to go live is implement the call site marked
`# TODO: replace stub with real Anthropic call`.

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

### 2. Run it

Use the launch script (top of this README) — it creates the Python virtualenv, installs
`requirements.txt`, runs `npm install`, and starts both servers. The commands below are only
needed if you prefer to run things by hand.

Manual backend (optional):

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

Manual frontend (optional): `npm --prefix frontend run dev` (Vite on http://localhost:5173,
proxies `/api` → `:8000`). Open the printed URL and click through the wizard. Every screen logs to
a per-session JSON file; in stub mode it works with no API key, and SQL execution returns a
neutral, handled message until the `.sqlite` files are present.

**Where the generated JSX goes (C3).** The model's call-1 output is `{ jsx, fields }`. The host
(`src/components/C3DynamicHost.jsx`) transpiles `jsx` with Babel-standalone and mounts it in the
bordered panel, injecting the primitive components (`src/components/c3primitives.jsx`) and
`submitResponses`. In stub mode a labelled grey **PLACEHOLDER** box is shown (no mock JSX is generated).
A non-empty `jsx` that fails to compile falls back to a labelled text-input form; only a genuinely
empty payload without `placeholder: true` shows that fallback.

### 4. Analysis (after sessions are collected)

```bash
jupyter notebook analysis/analysis.ipynb
```

---

## Going live (later, by the researcher)

1. Copy `backend/.env.example` → `backend/.env`; set `ANTHROPIC_API_KEY=...`. Optionally set
   `USE_STUB=False` to default to live (or just pick *Live API* on page 0 per session).
2. Replace the stub at the `# TODO: replace stub with real Anthropic call` site in
   `backend/calls/_stub.py` with a real `anthropic` Messages call. The stub already returns the
   same `.content[0].text` / `.usage` shape, so this is a one-spot change. (Until this is done,
   *Live API* will error and stub remains the working mode.)
3. Confirm `MODEL_NAME` in `backend/config.py` (currently `claude-opus-4-7`; a newer Opus may
   have shipped — bump it if so).

---

## A note on showing the SQL

The participant is shown the generated SQL next to a confident, results-referencing
explanation — even though, by design, they know nothing about SQL. This is a
deliberate overreliance probe, not decoration: the overreliance literature predicts
showing the "evidence" they cannot verify *widens* the perceived-vs-actual gap. What
stays hidden is whether the answer is actually **correct** — that is scored post-hoc
by the researcher in the notebook, never shown in-session.
