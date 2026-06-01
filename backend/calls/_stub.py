"""The stubbed model-call layer.

`complete()` is the single entry point every handler uses. With config.USE_STUB it
returns a canned payload whose shape matches the real Anthropic Messages response
(`.content[0].text`, `.usage.input_tokens/output_tokens`), so the whole apparatus runs
end to end with no API key. Flip USE_STUB to False and the marked branch issues the real
call — going live is genuinely one spot.

tenacity retry is wired now (around the call) per the build brief.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from backend import config

# ---------------------------------------------------------------------------
# Response shape — mirrors anthropic's Message just enough for our handlers.
# ---------------------------------------------------------------------------


@dataclass
class StubUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class StubBlock:
    text: str
    type: str = "text"


@dataclass
class StubMessage:
    content: list[StubBlock]
    usage: StubUsage
    model: str = config.MODEL_NAME
    stop_reason: str = "end_turn"


def _approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


@retry(
    stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=config.API_RETRY_BACKOFF_SECONDS),
    reraise=True,
)
def complete(
    *,
    kind: str,
    prompt: str,
    max_tokens: int,
    temperature: float = config.MODEL_TEMPERATURE,
    context: Optional[dict[str, Any]] = None,
    extra: Optional[dict[str, Any]] = None,
    use_stub: Optional[bool] = None,
) -> StubMessage:
    """Return a model completion.

    `use_stub` is the per-session choice from page 0 of the wizard; when it is None we fall
    back to the config default. When stubbed, `kind` selects the canned payload.
    """
    context = context or {}
    extra = extra or {}
    stubbed = config.USE_STUB if use_stub is None else use_stub

    if stubbed:
        text = _canned(kind, context, extra)
        return StubMessage(
            content=[StubBlock(text=text)],
            usage=StubUsage(
                input_tokens=_approx_tokens(prompt),
                output_tokens=_approx_tokens(text),
            ),
            model=config.MODEL_NAME,
        )

    # TODO: replace stub with real Anthropic call -----------------------------
    # The stub above returns the same .content/.usage shape, so this branch is the
    # only thing that changes to go live.
    import anthropic  # imported lazily, only when actually going live

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return client.messages.create(  # type: ignore[return-value]
        model=config.MODEL_NAME,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    # -------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Canned placeholder payloads (one per call `kind`)
#
# These return the minimum valid JSON that satisfies each call's pydantic contract,
# with placeholder=True so the frontend renders a labelled PLACEHOLDER box rather
# than any invented content. No mock widgets, no fabricated JSX.
# ---------------------------------------------------------------------------


def _canned_c3_bespoke(context: dict[str, Any]) -> str:
    # Empty jsx + placeholder=True → C3DynamicHost shows the grey PLACEHOLDER slot.
    payload = {"jsx": "", "fields": [], "placeholder": True}
    return json.dumps(payload)


def _canned_c2_static(context: dict[str, Any]) -> str:
    # Empty widgets + placeholder=True → C2StaticInterface shows a PLACEHOLDER box.
    payload = {"widgets": [], "allow_additional_constraints": False, "placeholder": True}
    return json.dumps(payload)


def _canned_query_sql(context: dict[str, Any]) -> str:
    db = context.get("db_name", "the database")
    question = context.get("question", "")
    # Table-free SELECT so it executes successfully against any SQLite database.
    sql = (
        "SELECT 'stub result' AS item, 42 AS value, "
        f"'{db} — live model disabled (USE_STUB=True)' AS note;"
    )
    payload = {
        "interpretation": f"(stub) Interpreting your question about {db}: {question[:120]}",
        "sql": sql,
    }
    return json.dumps(payload)


def _canned_query_explain(context: dict[str, Any], extra: dict[str, Any]) -> str:
    db = context.get("db_name", "the database")
    sql = extra.get("sql", "")
    row_count = extra.get("row_count", 0)
    payload = {
        "interpretation": f"(stub) Your request against the {db} records.",
        "sql": sql,
        "explanation": (
            f"(stub explanation) The system ran the request against the {db} records and "
            f"got back {row_count} result(s). This canned text stands in for the real "
            f"model's plain-language summary, which is generated once USE_STUB is False."
        ),
    }
    return json.dumps(payload)


def _canned_c1_baseline(context: dict[str, Any]) -> str:
    db = context.get("db_name", "the database")
    sql = (
        "SELECT 'c1 baseline (stub)' AS item, 1 AS value, "
        f"'{db}' AS note;"
    )
    return json.dumps({"sql": sql})


def _canned(kind: str, context: dict[str, Any], extra: dict[str, Any]) -> str:
    if kind == "c2_static":
        return _canned_c2_static(context)
    if kind == "c3_bespoke":
        return _canned_c3_bespoke(context)
    if kind == "query_sql":
        return _canned_query_sql(context)
    if kind == "query_explain":
        return _canned_query_explain(context, extra)
    if kind == "c1_baseline":
        return _canned_c1_baseline(context)
    raise ValueError(f"Unknown stub kind: {kind!r}")
