"""FastAPI backend for the student_club study.

Powers all three interface conditions from one model at temperature 0, using the
prompts in PROMPTS.md verbatim, and logs every interaction write-through to a
SQLite logging DB plus an append-only events.jsonl.

Window model: one message list per (session_id, question_index, condition). The
first call (A1/A2/A3) starts it; /api/finalize appends the finalise turn and
continues it. The full window is stored in model_calls.request_json so it is
auditable.
"""

import json
import os
import re
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Optional

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import content_db
import finalise as finalise_mod
import llm
import prompts
import store

# Condition order: randomisable for the real study, fixed default now.
DEFAULT_CONDITION_ORDER = ["1", "2", "3"]  # chatbot -> AmbiSQL -> dynamic
CONTRACT_VERSION = "1.0"

app = FastAPI(title="student_club study backend")

# CORS for the Vite dev origin(s).
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    store.init_db()


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class SessionStart(BaseModel):
    demographics: Optional[dict] = None
    condition_order: Optional[list] = None
    user_agent: Optional[str] = None


class QuestionsBody(BaseModel):
    session_id: str
    questions: list  # [{ index, text, submitted_at }]


class ChatBody(BaseModel):
    session_id: str
    question_index: int
    history: list  # [{ role, content }] — at least the person's question


class AmbiguitiesBody(BaseModel):
    session_id: str
    question_index: int
    question: str


class DynamicBody(BaseModel):
    session_id: str
    question_index: int
    question: str
    ambiguities: Optional[list] = None


class FinalizeBody(BaseModel):
    session_id: str
    question_index: int
    condition: str
    clarifications: Any = None


class ResolutionLogBody(BaseModel):
    session_id: str
    question_index: int
    log: dict


class FeedbackBody(BaseModel):
    session_id: str
    condition: str
    question_index: int
    q1: Optional[int] = None
    q2: Optional[int] = None
    text: Optional[str] = None


class LogBody(BaseModel):
    events: list


class SessionEnd(BaseModel):
    session_id: str


class DemographicsBody(BaseModel):
    session_id: str
    demographics: dict


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _model_turn(session_id, question_index, condition, call_type, system, messages):
    """Run one model turn, store the raw call, persist the window, return text."""
    try:
        out = llm.complete(system, messages)
    except Exception as exc:  # fail loud
        raise HTTPException(status_code=502, detail=f"Model call failed: {exc}")

    new_messages = messages + [{"role": "assistant", "content": out["text"]}]
    store.save_model_call(
        session_id, question_index, condition, call_type, llm.MODEL,
        request_json={"system": system, "messages": messages},
        response_json=out["response_json"],
        latency_ms=out["latency_ms"],
        prompt_tokens=out["prompt_tokens"],
        completion_tokens=out["completion_tokens"],
    )
    store.save_window(session_id, question_index, condition, system, new_messages)
    return out["text"]


def _extract_json(text: str):
    """Pull the first JSON object out of a model reply (tolerates stray prose)."""
    cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(cleaned[start:end + 1])
    raise ValueError("No JSON object found in model reply.")


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health():
    return {"ok": True, "model": llm.MODEL}


@app.post("/api/session/start")
def session_start(body: SessionStart):
    session_id = uuid.uuid4().hex
    order = body.condition_order or DEFAULT_CONDITION_ORDER
    store.upsert_session(session_id, body.demographics, order, body.user_agent)
    return {"session_id": session_id, "condition_order": order}


@app.post("/api/questions")
def questions(body: QuestionsBody):
    for q in body.questions:
        store.save_question(
            body.session_id, q.get("index"), q.get("text", ""), q.get("submitted_at")
        )
    return {"ok": True}


@app.post("/api/chat")
def chat(body: ChatBody):
    """C1, call A1. One clarifying turn — plain language, no SQL."""
    # Start (or continue) the C1 window from the supplied history.
    messages = [m for m in body.history if m.get("role") in ("user", "assistant")]
    if not messages:
        raise HTTPException(status_code=400, detail="history must contain the question.")
    reply = _model_turn(
        body.session_id, body.question_index, "1", "chat",
        prompts.A1_CHATBOT, messages,
    )
    return {"reply": reply}


@app.post("/api/ambiguities")
def ambiguities(body: AmbiguitiesBody):
    """C2, call A2. Returns { originalQuestion, summary, ambiguities[] }."""
    messages = [{"role": "user", "content": body.question}]
    text = _model_turn(
        body.session_id, body.question_index, "2", "ambiguities",
        prompts.A2_AMBIGUITY, messages,
    )
    try:
        spec = _extract_json(text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"A2 returned non-JSON: {exc}")
    spec.setdefault("originalQuestion", body.question)
    spec.setdefault("summary", "")
    spec.setdefault("ambiguities", [])
    spec.pop("databaseId", None)  # backend knows it
    return spec


@app.post("/api/dynamic")
def dynamic(body: DynamicBody):
    """C3, call A3. Returns component source only.

    Run A2 first if no ambiguity set was supplied, so the *ambiguity set* is held
    constant between C2 and C3 and only the *interface* varies.
    """
    ambiguities_list = body.ambiguities
    if ambiguities_list is None:
        a2_messages = [{"role": "user", "content": body.question}]
        a2_text = _model_turn(
            body.session_id, body.question_index, "3", "ambiguities_for_dynamic",
            prompts.A2_AMBIGUITY, a2_messages,
        )
        try:
            ambiguities_list = _extract_json(a2_text).get("ambiguities", [])
        except Exception:
            ambiguities_list = []
        # Reset the window so A3 is the first turn the finaliser sees for C3.
        store.save_window(body.session_id, body.question_index, "3", None, [])

    user_turn = prompts.a3_user(body.question, json.dumps(ambiguities_list))
    messages = [{"role": "user", "content": user_turn}]
    src = _model_turn(
        body.session_id, body.question_index, "3", "dynamic",
        prompts.A3_DYNAMIC, messages,
    )
    component_src = _clean_component_src(src)
    store.save_dynamic_ui(
        body.session_id, body.question_index, component_src, CONTRACT_VERSION
    )
    return {"component_src": component_src, "contract_version": CONTRACT_VERSION,
            "ambiguities": ambiguities_list}


def _clean_component_src(src: str) -> str:
    s = src.strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


@app.post("/api/finalize")
def finalize(body: FinalizeBody):
    """Finalise turn — appended to the condition's existing window."""
    system, messages = store.load_window(
        body.session_id, body.question_index, body.condition
    )
    if messages is None:
        # No window yet (e.g. C2 finalised without a prior call): start a minimal one.
        system = prompts.SYSTEM_BY_CONDITION.get(body.condition, prompts.A1_CHATBOT)
        messages = []

    clar_text = finalise_mod.serialise_clarifications(body.clarifications)
    messages = messages + [{"role": "user", "content": prompts.finalise_turn(clar_text)}]

    text = _model_turn(
        body.session_id, body.question_index, body.condition, "finalize",
        system, messages,
    )
    try:
        explanation, confidence, sql = finalise_mod.parse_finaliser(text)
    except finalise_mod.FinaliserFormatError as exc:
        raise HTTPException(status_code=502, detail=f"Finaliser malformed: {exc}")

    try:
        columns, all_rows, preview, total = content_db.run_select(sql)
    except content_db.SQLValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Rejected SQL: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"SQL failed to run: {exc}")

    store.save_response(
        body.session_id, body.question_index, body.condition,
        explanation, confidence, sql, total,
        result_json={"columns": columns, "rows": all_rows},
    )
    return {
        "explanation": explanation,
        "confidence": confidence,
        "sql": sql,
        "columns": columns,
        "preview_rows": preview,
        "total_count": total,
    }


@app.post("/api/resolution-log")
def resolution_log(body: ResolutionLogBody):
    store.save_resolution_log(body.session_id, body.question_index, body.log)
    return {"ok": True}


@app.post("/api/dynamic-status")
def dynamic_status(payload: dict):
    """Record whether the C3 UI rendered or fell back (additive to dynamic_ui)."""
    store.save_dynamic_ui(
        payload.get("session_id"), payload.get("question_index"),
        payload.get("component_src", ""), payload.get("contract_version", CONTRACT_VERSION),
        rendered_ok=1 if payload.get("rendered_ok") else 0,
        used_fallback=1 if payload.get("used_fallback") else 0,
    )
    return {"ok": True}


@app.post("/api/feedback")
def feedback(body: FeedbackBody):
    store.save_feedback(
        body.session_id, body.condition, body.question_index,
        body.q1, body.q2, body.text,
    )
    return {"ok": True}


@app.post("/api/log")
def log(body: LogBody):
    if not body.events:
        return {"ok": True, "written": 0}
    written = store.save_events(body.events)
    return {"ok": True, "written": written}


@app.post("/api/session/demographics")
def session_demographics(body: DemographicsBody):
    store.update_demographics(body.session_id, body.demographics)
    return {"ok": True}


@app.post("/api/session/end")
def session_end(body: SessionEnd):
    store.end_session(body.session_id)
    return {"ok": True}
