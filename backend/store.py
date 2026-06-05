"""Logging store — the highest-priority part of the instrument.

Two destinations, written on every event:
  1. a SQLite logging DB (separate file from the content DB), and
  2. an append-only events.jsonl backup (mirrors the events table).

Everything is write-through and fails loud: a write that cannot complete raises,
so a caller can return 5xx rather than silently dropping a person's question or
a model response.
"""

import json
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path

_HERE = Path(__file__).resolve().parent
LOG_DIR = Path(os.getenv("STUDY_LOG_DIR", _HERE / "logs"))
LOG_DB_PATH = LOG_DIR / "study_logs.sqlite"
EVENTS_JSONL = LOG_DIR / "events.jsonl"

# Per-process serialisation. SQLite handles concurrency, but a single lock keeps
# the jsonl append and the DB write atomic relative to one another.
_LOCK = threading.RLock()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time()*1000)%1000:03d}Z"


def _new_id() -> str:
    return uuid.uuid4().hex


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(LOG_DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  session_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  ended_at TEXT,
  demographics_json TEXT,
  condition_order_json TEXT,
  user_agent TEXT
);
CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  question_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  submitted_at TEXT
);
CREATE TABLE IF NOT EXISTS model_calls (
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
);
CREATE TABLE IF NOT EXISTS responses (
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
);
CREATE TABLE IF NOT EXISTS resolution_logs (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  question_index INTEGER,
  log_json TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dynamic_ui (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  question_index INTEGER,
  component_src TEXT,
  contract_version TEXT,
  rendered_ok INTEGER,
  used_fallback INTEGER,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feedback (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  condition TEXT,
  question_index INTEGER,
  q1 INTEGER,
  q2 INTEGER,
  text TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
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
);
-- Internal: the per-(session, question, condition) message window so the
-- finalise turn can continue the exact conversation the first call started.
CREATE TABLE IF NOT EXISTS message_windows (
  key TEXT PRIMARY KEY,
  session_id TEXT,
  question_index INTEGER,
  condition TEXT,
  messages_json TEXT NOT NULL,
  system_prompt TEXT,
  updated_at TEXT NOT NULL
);
"""


def init_db() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with _LOCK, _connect() as conn:
        conn.executescript(SCHEMA)
    EVENTS_JSONL.touch(exist_ok=True)


# --- write helpers (every one fails loud) -----------------------------------

def upsert_session(session_id, demographics, condition_order, user_agent) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO sessions (session_id, created_at, demographics_json, condition_order_json, user_agent)
               VALUES (?,?,?,?,?)
               ON CONFLICT(session_id) DO UPDATE SET
                 demographics_json=excluded.demographics_json,
                 condition_order_json=excluded.condition_order_json,
                 user_agent=excluded.user_agent""",
            (session_id, _now(), json.dumps(demographics), json.dumps(condition_order), user_agent),
        )


def end_session(session_id) -> None:
    with _LOCK, _connect() as conn:
        conn.execute("UPDATE sessions SET ended_at=? WHERE session_id=?", (_now(), session_id))


def update_demographics(session_id, demographics) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            "UPDATE sessions SET demographics_json=? WHERE session_id=?",
            (json.dumps(demographics), session_id),
        )


def save_question(session_id, question_index, text, submitted_at) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO questions (id, session_id, question_index, text, submitted_at)
               VALUES (?,?,?,?,?)""",
            (_new_id(), session_id, question_index, text, submitted_at),
        )


def save_model_call(session_id, question_index, condition, call_type, model,
                    request_json, response_json, latency_ms,
                    prompt_tokens, completion_tokens) -> str:
    cid = _new_id()
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO model_calls
               (id, session_id, question_index, condition, call_type, model,
                request_json, response_json, latency_ms, prompt_tokens,
                completion_tokens, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (cid, session_id, question_index, condition, call_type, model,
             json.dumps(request_json), json.dumps(response_json), latency_ms,
             prompt_tokens, completion_tokens, _now()),
        )
    return cid


def save_response(session_id, question_index, condition, explanation, confidence,
                  sql, row_count, result_json) -> str:
    rid = _new_id()
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO responses
               (id, session_id, question_index, condition, explanation, confidence,
                sql, row_count, result_json, correct, shown_at)
               VALUES (?,?,?,?,?,?,?,?,?,NULL,?)""",
            (rid, session_id, question_index, condition, explanation, confidence,
             sql, row_count, json.dumps(result_json), _now()),
        )
    return rid


def save_resolution_log(session_id, question_index, log_obj) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO resolution_logs (id, session_id, question_index, log_json, created_at)
               VALUES (?,?,?,?,?)""",
            (_new_id(), session_id, question_index, json.dumps(log_obj), _now()),
        )


def save_dynamic_ui(session_id, question_index, component_src, contract_version,
                    rendered_ok=None, used_fallback=None) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO dynamic_ui
               (id, session_id, question_index, component_src, contract_version,
                rendered_ok, used_fallback, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (_new_id(), session_id, question_index, component_src, contract_version,
             rendered_ok, used_fallback, _now()),
        )


def save_feedback(session_id, condition, question_index, q1, q2, text) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO feedback (id, session_id, condition, question_index, q1, q2, text, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (_new_id(), session_id, condition, question_index, q1, q2, text, _now()),
        )


def save_events(events: list) -> int:
    """Write a batch of interaction events to BOTH the DB and events.jsonl."""
    ts_server = _now()
    rows = []
    jsonl_lines = []
    for e in events:
        eid = _new_id()
        row = (
            eid,
            e.get("session_id"),
            e.get("screen"),
            e.get("condition"),
            e.get("question_index"),
            e.get("event_type") or e.get("type"),
            e.get("target_id"),
            json.dumps(e.get("value_json", e.get("value"))),
            e.get("ts_client"),
            ts_server,
            e.get("elapsed_ms"),
        )
        rows.append(row)
        jsonl_lines.append(json.dumps({
            "id": eid, "session_id": row[1], "screen": row[2], "condition": row[3],
            "question_index": row[4], "event_type": row[5], "target_id": row[6],
            "value_json": e.get("value_json", e.get("value")),
            "ts_client": row[8], "ts_server": ts_server, "elapsed_ms": row[10],
        }))
    with _LOCK:
        with _connect() as conn:
            conn.executemany(
                """INSERT INTO events
                   (id, session_id, screen, condition, question_index, event_type,
                    target_id, value_json, ts_client, ts_server, elapsed_ms)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                rows,
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
    with _LOCK, _connect() as conn:
        conn.execute(
            """INSERT INTO message_windows
               (key, session_id, question_index, condition, messages_json, system_prompt, updated_at)
               VALUES (?,?,?,?,?,?,?)
               ON CONFLICT(key) DO UPDATE SET
                 messages_json=excluded.messages_json,
                 system_prompt=excluded.system_prompt,
                 updated_at=excluded.updated_at""",
            (key, session_id, question_index, condition,
             json.dumps(messages), system_prompt, _now()),
        )


def load_window(session_id, question_index, condition):
    key = _window_key(session_id, question_index, condition)
    with _LOCK, _connect() as conn:
        row = conn.execute(
            "SELECT system_prompt, messages_json FROM message_windows WHERE key=?",
            (key,),
        ).fetchone()
    if not row:
        return None, None
    return row["system_prompt"], json.loads(row["messages_json"])


def table_counts() -> dict:
    out = {}
    with _LOCK, _connect() as conn:
        for t in ("sessions", "questions", "model_calls", "responses",
                  "resolution_logs", "dynamic_ui", "feedback", "events"):
            out[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return out
