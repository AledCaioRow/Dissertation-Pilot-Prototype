"""Call 2 handler (STUBBED model, REAL execution): generate SQL -> run -> explain.

"One-shot" is one human turn, not one API call. Behind a single participant submit this
folds three steps into the single logical call 2:

  1. generate {interpretation, sql} from the question + labelled clarifications,
  2. run_sql executes it locally (REAL), then
  3. the rows are fed back so the explanation references the ACTUAL result.

Going live, steps 1–3 become one tool-use completion (run_sql registered as the tool);
the structure here already hands the model the rows before it writes the explanation, so
the explanation is genuinely post-execution. There is no separate call 3.
"""
from __future__ import annotations

import time
from typing import Tuple

from backend import config
from backend.calls import _stub, extract_json_block, load_call_module, load_prompt
from backend.context.build_context import Context, format_clarifications
from backend.execution.run_sql import ExecutionResult, rows_as_text, run_sql
from backend.logging_io.call_log import CallLogRecord, build_record

_io = load_call_module("02_query_generation", "io")
QueryGenerationResult = _io.QueryGenerationResult
clean_sql = _io.clean_sql

_CALL = "02_query_generation"


def generate_query(
    context: Context,
    responses: list[dict],
    *,
    condition: str | None = None,
) -> Tuple["QueryGenerationResult", ExecutionResult, list[CallLogRecord]]:
    template = load_prompt(_CALL, "prompt.txt")
    clar = format_clarifications(responses)
    records: list[CallLogRecord] = []

    # --- Step 1: interpretation + SQL (rows not yet known) -------------------
    prompt_sql = template.format(
        schema_card=context.schema_card,
        question=context.question,
        clarifications=clar,
        row_count="(pending — query not yet run)",
        rows_sample="(the query has not been run yet)",
    )
    t0 = time.perf_counter()
    msg1 = _stub.complete(
        kind="query_sql", prompt=prompt_sql,
        max_tokens=config.MODEL_MAX_TOKENS_DEFAULT, context=context.as_dict(),
    )
    lat1 = int((time.perf_counter() - t0) * 1000)
    raw1 = msg1.content[0].text

    interpretation, sql, parsed_ok, parse_error = "", "", True, None
    try:
        step1 = _io_loads(raw1)
        interpretation = step1.get("interpretation", "")
        sql = clean_sql(step1.get("sql", ""))
    except Exception as exc:  # noqa: BLE001
        parsed_ok, parse_error = False, str(exc)
        sql = clean_sql(raw1)
    records.append(build_record(
        call=_CALL, kind="query_sql", prompt=prompt_sql, message=msg1, latency_ms=lat1,
        parsed_ok=parsed_ok, parse_error=parse_error, condition=condition,
    ))

    # --- Step 2: REAL execution ---------------------------------------------
    exec_result = run_sql(context.db_name, sql)

    # --- Step 3: explanation, now that the rows are known -------------------
    prompt_explain = template.format(
        schema_card=context.schema_card,
        question=context.question,
        clarifications=clar,
        row_count=exec_result.row_count if exec_result.success else 0,
        rows_sample=rows_as_text(exec_result),
    )
    t1 = time.perf_counter()
    msg2 = _stub.complete(
        kind="query_explain", prompt=prompt_explain,
        max_tokens=config.MODEL_MAX_TOKENS_DEFAULT, context=context.as_dict(),
        extra={"sql": sql, "row_count": exec_result.row_count, "success": exec_result.success},
    )
    lat2 = int((time.perf_counter() - t1) * 1000)
    raw2 = msg2.content[0].text

    explanation, parsed_ok2, parse_error2 = "", True, None
    try:
        step2 = _io_loads(raw2)
        explanation = step2.get("explanation", "")
        interpretation = step2.get("interpretation", interpretation) or interpretation
    except Exception as exc:  # noqa: BLE001
        parsed_ok2, parse_error2 = False, str(exc)
        explanation = raw2.strip()
    records.append(build_record(
        call=_CALL, kind="query_explain", prompt=prompt_explain, message=msg2, latency_ms=lat2,
        parsed_ok=parsed_ok2, parse_error=parse_error2, condition=condition,
    ))

    result = QueryGenerationResult(interpretation=interpretation, sql=sql, explanation=explanation)
    return result, exec_result, records


def _io_loads(raw: str) -> dict:
    import json
    return json.loads(extract_json_block(raw))
