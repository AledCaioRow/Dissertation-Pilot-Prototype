# student_club study instrument

An MSc-dissertation instrument comparing **three interface conditions** that help a
non-technical person get answers from a SQL database by clarifying ambiguous
plain-English questions:

- **C1 — Chatbot** (plain text, one clarifying turn)
- **C2 — AmbiSQL-inspired wizard** (fixed UI, one ambiguity at a time)
- **C3 — Dynamic** (the model generates the clarification UI itself, run sandboxed)

Two turns per condition in one context window: the first turn differs by condition
(text / JSON / code); the **finalise turn** is appended to that same window and writes
the SQL. Same model at temperature 0 for every call. The frozen `DB_CONTEXT.md` is
injected verbatim into every call so no condition is better-informed.

> Note: the pre-existing `app.py` Auto-MPG Streamlit demo at the repo root is left
> untouched and is unrelated to this study instrument, which lives under
> `backend/` and `frontend/`.

## Layout
```
backend/    FastAPI app, prompts (verbatim from PROMPTS.md), read-only content DB,
            logging system, smoke test + CSV export
frontend/   Vite + React study shell (StudyShell), the C2 wizard, the C1 chatbot,
            the sandboxed C3 host, and the shared output stage
```

## Backend — run steps
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then put your real ANTHROPIC_API_KEY in .env
uvicorn main:app --reload --port 8000
```
The content DB (`backend/data/student_club.sqlite`) is opened **read-only**; the
finaliser's SQL is validated as a single SELECT before it runs. Logs are written
write-through to `backend/logs/study_logs.sqlite` and mirrored to
`backend/logs/events.jsonl`.

Useful env vars (see `.env.example`): `STUDY_MODEL` (default `claude-sonnet-4-6`),
`STUDENT_CLUB_DB`, `STUDY_LOG_DIR`, `CORS_ORIGINS`.

### Self-verification (requires ANTHROPIC_API_KEY)
```bash
cd backend
python scripts/smoke_test.py
```
Runs the whole pipeline in-process (C1 + C2 + C3 + logging), prints a PASS/FAIL
row-count table for every logging table, and fails loud if any table is empty or a
model call returned non-conforming output.

### Export logs to CSV
```bash
cd backend
python scripts/export_csv.py            # writes logs/csv/*.csv
```

## Frontend — run steps
```bash
cd frontend
npm install
npm run dev                              # http://localhost:5173
```
`npm run dev`/`build` first copy the React + Babel UMD bundles into
`src/sandbox/vendor/` (via `scripts/copy-vendor.mjs`) so the C3 sandbox loads them
locally — never from a CDN. Point the frontend at a non-default backend with
`VITE_API_BASE`.

## Conditions & counterbalancing (open parameters)
- **Condition order** — randomisable; default fixed to chatbot → AmbiSQL → dynamic
  (`DEFAULT_CONDITION_ORDER` in `backend/main.py`).
- **Question → condition assignment** — `QUESTION_FOR_SLOT` in
  `frontend/src/StudyShell.jsx` (default identity).
- **SQL dialect** — `SQL_DIALECT` in `backend/prompts.py` (default `SQLite`, matches
  the content DB).

## What is NOT changed
`StudyShell.jsx`'s existing screens, navigation, back/exit buttons, layout and styling
are unchanged. Only the C1/C2/C3 interface placeholders and the output placeholder were
filled; logging is attached additively to existing controls.
