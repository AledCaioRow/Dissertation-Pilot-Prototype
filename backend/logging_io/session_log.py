"""The per-session JSON log, written incrementally from phase 1 onward.

One file per participant (`session_logs/p{ID}.json`). Every endpoint mutates the in-memory
SessionLog and immediately persists it, so a crash can resume from the last logged phase.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from backend import config
from backend.logging_io.call_log import CallLogRecord


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Trial(BaseModel):
    trial_id: str
    db_name: str
    ambiguity_class: str          # for the researcher's records; never shown
    condition: str                # "C2" | "C3"
    slot: int                     # class index within the schema (0/1)
    question: str = ""
    intent_note: str = ""         # locked pre-interaction; the scoring anchor
    # call 1 output:
    interface: Optional[dict[str, Any]] = None   # ClarificationData (C2) or {jsx, fields} (C3)
    compile_success: Optional[bool] = None       # C3 only; set by the frontend
    # participant submission (shared responses contract):
    responses: Optional[list[dict[str, Any]]] = None
    # call 2 output + execution:
    result: Optional[dict[str, Any]] = None       # {rows, column_names, sql, interpretation, explanation, success, error, row_count}
    # two-stage confidence:
    perceived_success: Optional[dict[str, Any]] = None
    # token/latency records for every model call in this trial:
    calls: list[CallLogRecord] = Field(default_factory=list)


class SessionLog(BaseModel):
    participant_id: int
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)
    assignment: dict[str, Any] = Field(default_factory=dict)
    consent: Optional[dict[str, Any]] = None
    screening: Optional[dict[str, Any]] = None
    trials: list[Trial] = Field(default_factory=list)
    questionnaires: list[dict[str, Any]] = Field(default_factory=list)  # per condition
    debrief: Optional[dict[str, Any]] = None
    withdrawn: bool = False
    complete: bool = False

    # --- trial helpers ---
    def trial(self, trial_id: str) -> Trial:
        for t in self.trials:
            if t.trial_id == trial_id:
                return t
        raise KeyError(f"No trial {trial_id!r} in session {self.participant_id}")


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _path(participant_id: int) -> Path:
    return config.session_log_dir() / f"p{participant_id}.json"


def exists(participant_id: int) -> bool:
    return _path(participant_id).exists()


def create_session(participant_id: int, assignment: dict[str, Any]) -> SessionLog:
    session = SessionLog(participant_id=participant_id, assignment=assignment)
    save_session(session)
    return session


def load_session(participant_id: int) -> SessionLog:
    path = _path(participant_id)
    if not path.exists():
        raise FileNotFoundError(f"No session log for participant {participant_id}")
    return SessionLog.model_validate_json(path.read_text(encoding="utf-8"))


def save_session(session: SessionLog) -> None:
    session.updated_at = _now()
    path = _path(session.participant_id)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(session.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic on POSIX
