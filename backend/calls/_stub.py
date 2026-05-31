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
import time
from dataclasses import dataclass, field
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
) -> StubMessage:
    """Return a model completion. `kind` selects the canned payload while stubbed."""
    context = context or {}
    extra = extra or {}

    if config.USE_STUB:
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
# Canned, correctly-shaped payloads (one per call `kind`)
# ---------------------------------------------------------------------------

# A self-contained component for the C3 sandbox: uses only injected primitives, is
# named `Interface`, and calls submitResponses(...) exactly once. Generic on purpose.
_STUB_C3_JSX = """
function Interface() {
  const [metric, setMetric] = React.useState('overall');
  const [threshold, setThreshold] = React.useState(50);
  const [matchAll, setMatchAll] = React.useState(true);
  const [note, setNote] = React.useState('');
  return (
    <div>
      <InfoPanel label="A few quick questions"
        help="Your answers help the system write exactly the request you mean." />
      <Radio id="metric" label="Which measure should count here?"
        value={metric} onChange={setMetric}
        options={[
          {value: 'overall', label: 'The overall, combined figure'},
          {value: 'single', label: 'A single specific figure'},
          {value: 'count', label: 'How many took part'}
        ]} />
      <Slider id="threshold" label="Only include results at or above this level"
        min={0} max={100} step={5} value={threshold} onChange={setThreshold} />
      <Toggle id="matchAll" label="Must every condition be met?"
        help="On = all of them, Off = any of them"
        value={matchAll} onChange={setMatchAll} />
      <TextInput id="note" label="Anything else to add? (optional)"
        value={note} onChange={setNote} />
      <button className="primary" onClick={() =>
        submitResponses({metric, threshold, matchAll, note})}>
        Show me the answer
      </button>
    </div>
  );
}
""".strip()


def _canned_c3_bespoke(context: dict[str, Any]) -> str:
    payload = {
        "jsx": _STUB_C3_JSX,
        "fields": [
            {"id": "metric", "label": "Which measure should count here?"},
            {"id": "threshold", "label": "Only include results at or above this level"},
            {"id": "matchAll", "label": "Must every condition be met? (all vs any)"},
            {"id": "note", "label": "Anything else to add?"},
        ],
    }
    return json.dumps(payload)


def _canned_c2_static(context: dict[str, Any]) -> str:
    payload = {
        "widgets": [
            {
                "id": "amb_1",
                "ambiguity_type": "unclear_schema_reference",
                "title": "Which figure should we use to compare?",
                "description": "There are several numbers we could rank or compare by.",
                "options": [
                    {"value": "overall", "label": "The overall, combined figure",
                     "snippet": "e.g. a total across several score columns"},
                    {"value": "single", "label": "A single specific figure",
                     "snippet": "e.g. one score column on its own"},
                    {"value": "count", "label": "How many took part",
                     "snippet": "e.g. a count of records"},
                ],
            },
            {
                "id": "amb_2",
                "ambiguity_type": "unclear_value_reference",
                "title": "How should we match the place or category you mentioned?",
                "description": "It could be stored in more than one way.",
                "options": [
                    {"value": "broad", "label": "The broader grouping",
                     "snippet": "e.g. a county / region column"},
                    {"value": "narrow", "label": "The narrower one",
                     "snippet": "e.g. a city / specific column"},
                ],
            },
        ],
        "allow_additional_constraints": True,
    }
    return json.dumps(payload)


def _canned_query_sql(context: dict[str, Any]) -> str:
    db = context.get("db_name", "the database")
    question = context.get("question", "")
    # A table-free SELECT so it executes successfully against ANY sqlite database
    # (even before the real BIRD files are present), keeping the demo runnable.
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
