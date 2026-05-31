"""Per-call log record: tokens, latency, the verbatim prompt, the raw response.

These records are the inputs to the C2-vs-C3 cost comparison (tokens/latency) and to the
C3 compile-success rate. One record per model completion; call 2 may produce two (sql then
explanation) — both tagged call="02_query_generation".
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel

from backend import config


class CallLogRecord(BaseModel):
    call: str                      # "01_interface_generation" | "02_query_generation" | "c1_baseline"
    kind: str                      # the stub kind / logical step
    condition: Optional[str] = None  # "C1" | "C2" | "C3"
    prompt: Optional[str] = None   # verbatim if config.LOG_PROMPTS_VERBATIM
    raw_response: str = ""
    parsed_ok: bool = True
    parse_error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    compile_success: Optional[bool] = None  # set later by the frontend for C3
    timestamp: str = ""


def build_record(
    *,
    call: str,
    kind: str,
    prompt: str,
    message: Any,
    latency_ms: int,
    parsed_ok: bool = True,
    parse_error: Optional[str] = None,
    condition: Optional[str] = None,
) -> CallLogRecord:
    """Construct a CallLogRecord from a (stub or real) message response."""
    usage = getattr(message, "usage", None)
    text = ""
    content = getattr(message, "content", None)
    if content:
        text = getattr(content[0], "text", "") or ""
    return CallLogRecord(
        call=call,
        kind=kind,
        condition=condition,
        prompt=prompt if config.LOG_PROMPTS_VERBATIM else None,
        raw_response=text,
        parsed_ok=parsed_ok,
        parse_error=parse_error,
        input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
        output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
        latency_ms=latency_ms,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
