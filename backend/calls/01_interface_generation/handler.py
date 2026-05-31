"""Call 1 handlers (STUBBED): detect ambiguities (C2) / generate a bespoke interface (C3).

Each handler loads its runtime prompt, formats the shared context in, issues the (stubbed)
completion, parses first-`{`-to-last-`}` JSON, validates with pydantic, and returns the
validated object alongside a CallLogRecord. On a parse/validation failure it returns a safe
default (empty widgets for C2; empty interface for C3) with parsed_ok=False so the session
can still proceed (build brief §11) — the raw response is preserved in the record.
"""
from __future__ import annotations

import time
from typing import Tuple

from backend import config
from backend.calls import _stub, extract_json_block, load_call_module, load_prompt, primitives_block
from backend.context.build_context import Context
from backend.logging_io.call_log import CallLogRecord, build_record

_io = load_call_module("01_interface_generation", "io")
ClarificationData = _io.ClarificationData
BespokeInterface = _io.BespokeInterface

_CALL = "01_interface_generation"


def generate_interface_c2(context: Context) -> Tuple["ClarificationData", CallLogRecord]:
    template = load_prompt(_CALL, "prompt_c2_static.txt")
    prompt = template.format(schema_card=context.schema_card, question=context.question)

    t0 = time.perf_counter()
    msg = _stub.complete(
        kind="c2_static",
        prompt=prompt,
        max_tokens=config.MODEL_MAX_TOKENS_INTERFACE_GEN,
        context=context.as_dict(),
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    raw = msg.content[0].text

    try:
        data = ClarificationData.model_validate_json(extract_json_block(raw))
        record = build_record(
            call=_CALL, kind="c2_static", prompt=prompt, message=msg,
            latency_ms=latency_ms, condition="C2",
        )
        return data, record
    except Exception as exc:  # noqa: BLE001
        record = build_record(
            call=_CALL, kind="c2_static", prompt=prompt, message=msg, latency_ms=latency_ms,
            parsed_ok=False, parse_error=str(exc), condition="C2",
        )
        # Empty widgets => the session skips the interaction and goes straight to call 2.
        return ClarificationData(widgets=[], allow_additional_constraints=True), record


def generate_interface_c3(context: Context) -> Tuple["BespokeInterface", CallLogRecord]:
    template = load_prompt(_CALL, "prompt_c3_bespoke.txt")
    prompt = template.format(
        schema_card=context.schema_card,
        question=context.question,
        primitives=primitives_block(),
    )

    t0 = time.perf_counter()
    msg = _stub.complete(
        kind="c3_bespoke",
        prompt=prompt,
        max_tokens=config.MODEL_MAX_TOKENS_INTERFACE_GEN,
        context=context.as_dict(),
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    raw = msg.content[0].text

    try:
        data = BespokeInterface.model_validate_json(extract_json_block(raw))
        record = build_record(
            call=_CALL, kind="c3_bespoke", prompt=prompt, message=msg,
            latency_ms=latency_ms, condition="C3",
        )
        return data, record
    except Exception as exc:  # noqa: BLE001
        record = build_record(
            call=_CALL, kind="c3_bespoke", prompt=prompt, message=msg, latency_ms=latency_ms,
            parsed_ok=False, parse_error=str(exc), condition="C3",
        )
        # Empty jsx => the host renders its manifest text-input fallback (compile_success=false).
        return BespokeInterface(jsx="", fields=[]), record
