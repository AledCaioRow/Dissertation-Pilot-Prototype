"""C1 condition — the no-human baseline. Run POST-HOC in the analysis notebook only.

C1 is one call (shared context -> SQL) plus execution: no interface, no human turn, no
participant-facing explanation. It answers each of the four authored questions directly,
so the notebook can compare "model alone" against the C2/C3 human-in-the-loop trials.
STUBBED model; REAL execution.
"""
from __future__ import annotations

import time

from backend import config
from backend.calls import _stub, extract_json_block
from backend.context.build_context import build_context
from backend.execution.run_sql import ExecutionResult, run_sql
from backend.logging_io.call_log import CallLogRecord, build_record

CONDITION = "C1"

_C1_PROMPT = """You turn a user's question into one correct SQLite query, using only the schema below.

Schema:
{schema_card}

Question:
{question}

Return ONLY this JSON object, no preamble:
{{"sql": "<single SQLite query>"}}
"""


def run_baseline(db_name: str, question: str, *, use_stub: bool | None = None) -> dict:
    """Answer one authored question with no human. Returns sql, execution, and the call log."""
    context = build_context(db_name, question)
    prompt = _C1_PROMPT.format(schema_card=context.schema_card, question=question)

    t0 = time.perf_counter()
    msg = _stub.complete(
        kind="c1_baseline", prompt=prompt,
        max_tokens=config.MODEL_MAX_TOKENS_DEFAULT, context=context.as_dict(),
        use_stub=use_stub,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    raw = msg.content[0].text

    parsed_ok, parse_error, sql = True, None, ""
    try:
        import json
        sql = json.loads(extract_json_block(raw)).get("sql", "")
    except Exception as exc:  # noqa: BLE001
        parsed_ok, parse_error, sql = False, str(exc), raw.strip()

    exec_result: ExecutionResult = run_sql(db_name, sql)
    record: CallLogRecord = build_record(
        call="c1_baseline", kind="c1_baseline", prompt=prompt, message=msg,
        latency_ms=latency_ms, parsed_ok=parsed_ok, parse_error=parse_error, condition="C1",
    )
    return {
        "db_name": db_name,
        "question": question,
        "sql": sql,
        "execution": exec_result.model_dump(),
        "call": record.model_dump(),
    }
