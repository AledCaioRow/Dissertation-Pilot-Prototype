"""Logging store — the highest-priority part of the instrument.

Participant data is written to a SQL database via SQLAlchemy, so the same code
runs against two backends with identical SQL:

  * **Local dev** (no ``DATABASE_URL``): a SQLite file under ``STUDY_LOG_DIR`` —
    zero setup, run the app straight away.
  * **Deployed / online** (``DATABASE_URL`` set): a managed Postgres database, so
    participant data lives in a proper database that survives app restarts and
    redeploys (see DEPLOY.md).

Every event is also mirrored to an append-only ``events.jsonl`` as a secondary
backup. Writes are write-through and fail loud: a write that cannot complete
raises, so a caller can return 5xx rather than silently dropping a person's
question or a model response.

NOTE: the *content* database (``content_db.py``, the read-only student_club data
the SQL runs against) stays on SQLite — only this participant-logging store uses
``DATABASE_URL``.
"""

import csv
import io
import json
import os
import threading
import time
import uuid
import zipfile
from pathlib import Path

from sqlalchemy import create_engine, event, text

_HERE = Path(__file__).resolve().parent
LOG_DIR = Path(os.getenv("STUDY_LOG_DIR", _HERE / "logs"))
EVENTS_JSONL = LOG_DIR / "events.jsonl"


def _resolve_database_url() -> str:
    """Postgres if DATABASE_URL is set (deployed), else a local SQLite file."""
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        # Render hands out 'postgres://…'; SQLAlchemy + psycopg3 wants
        # 'postgresql+psycopg://…'. Normalise either Postgres prefix.
        if url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and "+psycopg" not in url:
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        return url
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(LOG_DIR / 'study_logs.sqlite').as_posix()}"


DATABASE_URL = _resolve_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# One engine per process. For SQLite, allow connections across the server's
# threads (writes are serialised by _LOCK below). pool_pre_ping keeps Postgres
# connections healthy across idle periods.
_connect_args = {"check_same_thread": False} if IS_SQLITE else {}
engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, future=True, connect_args=_connect_args
)

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_conn, _record):  # pragma: no cover - trivial
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA foreign_keys=ON;")
        cur.close()

# Per-process lock keeps each events batch's DB write and its jsonl append atomic
# relative to one another.
_LOCK = threading.RLock()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time()*1000)%1000:03d}Z"


def _new_id() -> str:
    return uuid.uuid4().hex


# Standard SQL that runs on both SQLite and Postgres (TEXT/INTEGER columns,
# TEXT-uuid primary keys, ON CONFLICT … DO UPDATE upserts).
SCHEMA_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS sessions (
      session_id TEXT PRIMARY KEY,
      created_at TEXT NOT NULL,
      ended_at TEXT,
      demographics_json TEXT,
      condition_order_json TEXT,
      user_agent TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS questions (
      id TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      question_index INTEGER NOT NULL,
      text TEXT NOT NULL,
      submitted_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS model_calls (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      question_index INTEGER,
      condition TEXT,
      call_type TEXT,
      model TEXT,
      request_json TEXT,
      response_json TEXT,
      latency_ms INTEGER,
      prompt_tokens INTEGER,
      completion_tokens INTEGER,
      created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS responses (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      question_index INTEGER,
      condition TEXT,
      explanation TEXT,
      confidence INTEGER,
      sql TEXT,
      row_count INTEGER,
      result_json TEXT,
      correct INTEGER,
      shown_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS resolution_logs (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      question_index INTEGER,
      log_json TEXT,
      created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS dynamic_ui (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      question_index INTEGER,
      component_src TEXT,
      contract_version TEXT,
      rendered_ok INTEGER,
      used_fallback INTEGER,
      created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS feedback (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      condition TEXT,
      question_index INTEGER,
      q1 INTEGER,
      q2 INTEGER,
      text TEXT,
      created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS events (
      id TEXT PRIMARY KEY,
      session_id TEXT,
      screen TEXT,
      condition TEXT,
      question_index INTEGER,
      event_type TEXT,
      target_id TEXT,
      value_json TEXT,
      ts_client TEXT,
      ts_server TEXT NOT NULL,
      elapsed_ms INTEGER
    )""",
    # Internal: the per-(session, question, condition) message window so the
    # finalise turn can continue the exact conversation the first call started.
    """CREATE TABLE IF NOT EXISTS message_windows (
      key TEXT PRIMARY KEY,
      session_id TEXT,
      question_index INTEGER,
      condition TEXT,
      messages_json TEXT NOT NULL,
      system_prompt TEXT,
      updated_at TEXT NOT NULL
    )""",
]

# The participant-facing tables, in a stable order, for CSV export and counts.
EXPORT_TABLES = [
    "sessions", "questions", "model_calls", "responses",
    "resolution_logs", "dynamic_ui", "feedback", "events",
]


def init_db() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with _LOCK, engine.begin() as conn:
        for stmt in SCHEMA_STATEMENTS:
            conn.exec_driver_sql(stmt)
    EVENTS_JSONL.touch(exist_ok=True)


def ping() -> bool:
    """True if the database is reachable (used by /api/health)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


# --- write helpers (every one fails loud) -----------------------------------

def upsert_session(session_id, demographics, condition_order, user_agent) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO sessions (session_id, created_at, demographics_json, condition_order_json, user_agent)
                   VALUES (:session_id, :created_at, :demographics_json, :condition_order_json, :user_agent)
                   ON CONFLICT(session_id) DO UPDATE SET
                     demographics_json=excluded.demographics_json,
                     condition_order_json=excluded.condition_order_json,
                     user_agent=excluded.user_agent"""
            ),
            {
                "session_id": session_id, "created_at": _now(),
                "demographics_json": json.dumps(demographics),
                "condition_order_json": json.dumps(condition_order),
                "user_agent": user_agent,
            },
        )


def end_session(session_id) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text("UPDATE sessions SET ended_at=:ended_at WHERE session_id=:session_id"),
            {"ended_at": _now(), "session_id": session_id},
        )


def update_demographics(session_id, demographics) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text("UPDATE sessions SET demographics_json=:d WHERE session_id=:session_id"),
            {"d": json.dumps(demographics), "session_id": session_id},
        )


def save_question(session_id, question_index, text_value, submitted_at) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO questions (id, session_id, question_index, text, submitted_at)
                   VALUES (:id, :session_id, :question_index, :text, :submitted_at)"""
            ),
            {
                "id": _new_id(), "session_id": session_id,
                "question_index": question_index, "text": text_value,
                "submitted_at": submitted_at,
            },
        )


def save_model_call(session_id, question_index, condition, call_type, model,
                    request_json, response_json, latency_ms,
                    prompt_tokens, completion_tokens) -> str:
    cid = _new_id()
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO model_calls
                   (id, session_id, question_index, condition, call_type, model,
                    request_json, response_json, latency_ms, prompt_tokens,
                    completion_tokens, created_at)
                   VALUES (:id, :session_id, :question_index, :condition, :call_type, :model,
                    :request_json, :response_json, :latency_ms, :prompt_tokens,
                    :completion_tokens, :created_at)"""
            ),
            {
                "id": cid, "session_id": session_id, "question_index": question_index,
                "condition": condition, "call_type": call_type, "model": model,
                "request_json": json.dumps(request_json),
                "response_json": json.dumps(response_json),
                "latency_ms": latency_ms, "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens, "created_at": _now(),
            },
        )
    return cid


def save_response(session_id, question_index, condition, explanation, confidence,
                  sql, row_count, result_json) -> str:
    rid = _new_id()
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO responses
                   (id, session_id, question_index, condition, explanation, confidence,
                    sql, row_count, result_json, correct, shown_at)
                   VALUES (:id, :session_id, :question_index, :condition, :explanation, :confidence,
                    :sql, :row_count, :result_json, NULL, :shown_at)"""
            ),
            {
                "id": rid, "session_id": session_id, "question_index": question_index,
                "condition": condition, "explanation": explanation, "confidence": confidence,
                "sql": sql, "row_count": row_count, "result_json": json.dumps(result_json),
                "shown_at": _now(),
            },
        )
    return rid


def save_resolution_log(session_id, question_index, log_obj) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO resolution_logs (id, session_id, question_index, log_json, created_at)
                   VALUES (:id, :session_id, :question_index, :log_json, :created_at)"""
            ),
            {
                "id": _new_id(), "session_id": session_id,
                "question_index": question_index, "log_json": json.dumps(log_obj),
                "created_at": _now(),
            },
        )


def save_dynamic_ui(session_id, question_index, component_src, contract_version,
                    rendered_ok=None, used_fallback=None) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO dynamic_ui
                   (id, session_id, question_index, component_src, contract_version,
                    rendered_ok, used_fallback, created_at)
                   VALUES (:id, :session_id, :question_index, :component_src, :contract_version,
                    :rendered_ok, :used_fallback, :created_at)"""
            ),
            {
                "id": _new_id(), "session_id": session_id,
                "question_index": question_index, "component_src": component_src,
                "contract_version": contract_version, "rendered_ok": rendered_ok,
                "used_fallback": used_fallback, "created_at": _now(),
            },
        )


def save_feedback(session_id, condition, question_index, q1, q2, text_value) -> None:
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO feedback (id, session_id, condition, question_index, q1, q2, text, created_at)
                   VALUES (:id, :session_id, :condition, :question_index, :q1, :q2, :text, :created_at)"""
            ),
            {
                "id": _new_id(), "session_id": session_id, "condition": condition,
                "question_index": question_index, "q1": q1, "q2": q2,
                "text": text_value, "created_at": _now(),
            },
        )


def save_events(events: list) -> int:
    """Write a batch of interaction events to BOTH the DB and events.jsonl."""
    ts_server = _now()
    rows = []
    jsonl_lines = []
    for e in events:
        eid = _new_id()
        value = e.get("value_json", e.get("value"))
        rows.append({
            "id": eid,
            "session_id": e.get("session_id"),
            "screen": e.get("screen"),
            "condition": e.get("condition"),
            "question_index": e.get("question_index"),
            "event_type": e.get("event_type") or e.get("type"),
            "target_id": e.get("target_id"),
            "value_json": json.dumps(value),
            "ts_client": e.get("ts_client"),
            "ts_server": ts_server,
            "elapsed_ms": e.get("elapsed_ms"),
        })
        jsonl_lines.append(json.dumps({
            "id": eid, "session_id": e.get("session_id"), "screen": e.get("screen"),
            "condition": e.get("condition"), "question_index": e.get("question_index"),
            "event_type": e.get("event_type") or e.get("type"), "target_id": e.get("target_id"),
            "value_json": value, "ts_client": e.get("ts_client"),
            "ts_server": ts_server, "elapsed_ms": e.get("elapsed_ms"),
        }))
    if not rows:
        return 0
    with _LOCK:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """INSERT INTO events
                       (id, session_id, screen, condition, question_index, event_type,
                        target_id, value_json, ts_client, ts_server, elapsed_ms)
                       VALUES (:id, :session_id, :screen, :condition, :question_index, :event_type,
                        :target_id, :value_json, :ts_client, :ts_server, :elapsed_ms)"""
                ),
                rows,  # list of dicts -> executemany
            )
        # Mirror to the append-only backup. If this fails, the whole call fails.
        with open(EVENTS_JSONL, "a", encoding="utf-8") as fh:
            for line in jsonl_lines:
                fh.write(line + "\n")
    return len(rows)


# --- message windows (internal, per condition) ------------------------------

def _window_key(session_id, question_index, condition) -> str:
    return f"{session_id}::{question_index}::{condition}"


def save_window(session_id, question_index, condition, system_prompt, messages) -> None:
    key = _window_key(session_id, question_index, condition)
    with _LOCK, engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO message_windows
                   (key, session_id, question_index, condition, messages_json, system_prompt, updated_at)
                   VALUES (:key, :session_id, :question_index, :condition, :messages_json, :system_prompt, :updated_at)
                   ON CONFLICT(key) DO UPDATE SET
                     messages_json=excluded.messages_json,
                     system_prompt=excluded.system_prompt,
                     updated_at=excluded.updated_at"""
            ),
            {
                "key": key, "session_id": session_id, "question_index": question_index,
                "condition": condition, "messages_json": json.dumps(messages),
                "system_prompt": system_prompt, "updated_at": _now(),
            },
        )


def load_window(session_id, question_index, condition):
    key = _window_key(session_id, question_index, condition)
    with _LOCK, engine.connect() as conn:
        row = conn.execute(
            text("SELECT system_prompt, messages_json FROM message_windows WHERE key=:key"),
            {"key": key},
        ).fetchone()
    if not row:
        return None, None
    return row.system_prompt, json.loads(row.messages_json)


def table_counts() -> dict:
    out = {}
    with _LOCK, engine.connect() as conn:
        for t in EXPORT_TABLES:
            out[t] = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
    return out


def export_csv_zip() -> bytes:
    """Return a .zip with one CSV per logging table (works on SQLite or Postgres)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        with engine.connect() as conn:
            for t in EXPORT_TABLES:
                result = conn.execute(text(f"SELECT * FROM {t}"))
                cols = list(result.keys())
                sio = io.StringIO()
                writer = csv.writer(sio)
                writer.writerow(cols)
                for r in result:
                    writer.writerow(list(r))
                zf.writestr(f"{t}.csv", sio.getvalue())
    return buf.getvalue()
