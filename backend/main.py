"""FastAPI session endpoints (build brief §6).

Thin and delegating: conditions own call 1, the call-2 handler is shared, and every
endpoint validates with pydantic and persists the per-session log immediately so a crash
can resume from the last logged phase. State is keyed by participant_id.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import config
from backend.calls import load_call_module
from backend.conditions import c2_static, c3_bespoke
from backend.context.build_context import build_context
from backend.counterbalance.assign import assign, describe
from backend.logging_io import session_log as slog
from backend.logging_io.session_log import Trial
from backend.schema.load_schema import load_schema

_qg = load_call_module("02_query_generation", "handler")

app = FastAPI(title="hitl-text-to-sql session API")

# Dev convenience: the Vite dev server runs on a different port. Tighten for deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _session(participant_id: int) -> slog.SessionLog:
    try:
        return slog.load_session(participant_id)
    except FileNotFoundError:
        raise HTTPException(404, f"No session for participant {participant_id}; call /session/start first")


def _guard_active(session: slog.SessionLog) -> None:
    if session.withdrawn:
        raise HTTPException(409, "Session has been withdrawn; no further screens.")


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class StartReq(BaseModel):
    participant_id: int


class ModeReq(BaseModel):
    participant_id: int
    use_stub: bool  # page 0: True = canned stub responses, False = live Anthropic call


class ConsentReq(BaseModel):
    participant_id: int
    name: str = ""
    email: str = ""
    consent: dict[str, bool] = {}
    agreed: bool = False


class ScreeningReq(BaseModel):
    participant_id: int
    age_band: str = ""
    sql_experience: str = ""
    db_experience: str = ""
    extra: dict[str, Any] = {}


class AuthorReq(BaseModel):
    participant_id: int
    db_name: str
    ambiguity_class: str
    question: str
    intent_note: str = ""


class InterfaceReq(BaseModel):
    participant_id: int
    trial_id: str


class AnswerReq(BaseModel):
    participant_id: int
    trial_id: str
    responses: list[dict[str, Any]] = []
    compile_success: Optional[bool] = None  # C3: did the generated JSX mount?


class PerceivedReq(BaseModel):
    participant_id: int
    trial_id: str
    interface_confidence: Optional[str] = None   # pre-result
    answer_wanted: Optional[str] = None           # post-result yes/no
    answer_confidence: Optional[str] = None       # post-result scale


class QuestionnaireReq(BaseModel):
    participant_id: int
    condition: str
    sus: dict[str, int] = {}
    agency: dict[str, int] = {}
    open_ended: dict[str, str] = {}


class DebriefReq(BaseModel):
    participant_id: int
    preference: str = ""
    open_ended: dict[str, str] = {}


class WithdrawReq(BaseModel):
    participant_id: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
def root() -> dict:
    return {"ok": True, "service": "hitl-text-to-sql", "stubbed": config.USE_STUB}


@app.get("/config")
def get_config() -> dict:
    """The handful of constants the frontend needs (keeps copy/behaviour tunable in one place)."""
    return {
        "loading_screen_min_seconds": config.LOADING_SCREEN_MIN_SECONDS,
        "question_authoring_min_chars": config.QUESTION_AUTHORING_MIN_CHARS,
        "show_result_row_limit": config.SHOW_RESULT_ROW_LIMIT,
        "stubbed": config.USE_STUB,
    }


@app.post("/session/start")
def session_start(req: StartReq) -> dict:
    assignment = assign(req.participant_id)
    if slog.exists(req.participant_id):
        # Resume an interrupted session rather than clobbering it (build brief §11).
        session = slog.load_session(req.participant_id)
    else:
        session = slog.create_session(req.participant_id, assignment.model_dump())
    print(describe(assignment))
    return {
        "assignment": assignment.model_dump(),
        "describe": describe(assignment),
        "resumed": bool(session.consent),
    }


@app.post("/session/mode")
def session_mode(req: ModeReq) -> dict:
    """Page 0: choose the model-call mode for this whole session (stub vs live API)."""
    session = _session(req.participant_id)
    _guard_active(session)
    session.use_stub = req.use_stub
    slog.save_session(session)
    print(f"[mode] participant {req.participant_id} -> {'STUB' if req.use_stub else 'LIVE API'}")
    return {"ok": True, "use_stub": session.use_stub}


@app.post("/session/consent")
def session_consent(req: ConsentReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    session.consent = req.model_dump(exclude={"participant_id"})
    slog.save_session(session)
    return {"ok": True}


@app.post("/session/screening")
def session_screening(req: ScreeningReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    session.screening = req.model_dump(exclude={"participant_id"})
    slog.save_session(session)
    return {"ok": True}


@app.get("/schema/{name}")
def get_schema(name: str) -> dict:
    if name not in config.DATABASES:
        raise HTTPException(404, f"Unknown database {name!r}")
    return load_schema(name).model_dump()


@app.post("/author")
def author(req: AuthorReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    if req.db_name not in config.DATABASES:
        raise HTTPException(400, f"Unknown database {req.db_name!r}")

    classes = config.SCHEMA_CLASS_MAP.get(req.db_name, [])
    slot = classes.index(req.ambiguity_class) if req.ambiguity_class in classes else 0
    condition = session.assignment.get("slot_to_condition", {}).get(
        f"{req.db_name}:{req.ambiguity_class}", "C2"
    )
    trial_id = f"p{req.participant_id}_t{len(session.trials) + 1}"

    session.trials.append(
        Trial(
            trial_id=trial_id,
            db_name=req.db_name,
            ambiguity_class=req.ambiguity_class,
            condition=condition,
            slot=slot,
            question=req.question,
            intent_note=req.intent_note,
        )
    )
    slog.save_session(session)
    return {"trial_id": trial_id, "condition": condition}


@app.post("/trial/interface")
def trial_interface(req: InterfaceReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    try:
        trial = session.trial(req.trial_id)
    except KeyError:
        raise HTTPException(404, f"No trial {req.trial_id}")

    context = build_context(trial.db_name, trial.question)
    if trial.condition == "C3":
        interface, record = c3_bespoke.run_interface(context, use_stub=session.use_stub)
    else:
        interface, record = c2_static.run_interface(context, use_stub=session.use_stub)

    trial.interface = interface.model_dump()
    trial.calls.append(record)
    slog.save_session(session)
    return {"condition": trial.condition, "data": trial.interface}


@app.post("/trial/answer")
def trial_answer(req: AnswerReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    try:
        trial = session.trial(req.trial_id)
    except KeyError:
        raise HTTPException(404, f"No trial {req.trial_id}")

    context = build_context(trial.db_name, trial.question)
    result, execution, records = _qg.generate_query(
        context, req.responses, condition=trial.condition, use_stub=session.use_stub
    )

    trial.responses = req.responses
    if req.compile_success is not None:
        trial.compile_success = req.compile_success
        # also reflect on the C3 call-1 record for the cost/compile analysis
        for rec in trial.calls:
            if rec.kind == "c3_bespoke":
                rec.compile_success = req.compile_success
    trial.calls.extend(records)

    payload = {
        "interpretation": result.interpretation,
        "sql": result.sql,
        "explanation": result.explanation,
        "rows": execution.rows,
        "column_names": execution.column_names,
        "success": execution.success,
        "error": execution.error,
        "row_count": execution.row_count,
    }
    trial.result = payload
    slog.save_session(session)
    return payload


@app.post("/trial/perceived")
def trial_perceived(req: PerceivedReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    try:
        trial = session.trial(req.trial_id)
    except KeyError:
        raise HTTPException(404, f"No trial {req.trial_id}")
    trial.perceived_success = req.model_dump(exclude={"participant_id", "trial_id"})
    slog.save_session(session)
    return {"ok": True}


@app.post("/questionnaire")
def questionnaire(req: QuestionnaireReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    session.questionnaires.append(req.model_dump(exclude={"participant_id"}))
    slog.save_session(session)
    return {"ok": True}


@app.post("/debrief")
def debrief(req: DebriefReq) -> dict:
    session = _session(req.participant_id)
    _guard_active(session)
    session.debrief = req.model_dump(exclude={"participant_id"})
    session.complete = True
    slog.save_session(session)
    return {"ok": True}


@app.post("/session/withdraw")
def session_withdraw(req: WithdrawReq) -> dict:
    """The persistent 'Exit and withdraw' control: mark the log withdrawn, stop screens."""
    session = _session(req.participant_id)
    session.withdrawn = True
    slog.save_session(session)
    return {"ok": True, "withdrawn": True}
