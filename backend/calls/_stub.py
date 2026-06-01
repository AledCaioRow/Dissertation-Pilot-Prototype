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
# Canned, correctly-shaped payloads (one per call `kind`)
# ---------------------------------------------------------------------------

# Realistic, db-specific C3 interfaces for the demo. Each is a self-contained component
# named `Interface`, uses only the injected primitives, and calls submitResponses(...) once.
# These stand in for what the live model would generate per question.

_STUB_C3_JSX_SCHOOLS = """
function Interface() {
  const [metric, setMetric] = React.useState('combined');
  const [region, setRegion] = React.useState('all');
  const [topN, setTopN] = React.useState(5);
  const [completeOnly, setCompleteOnly] = React.useState(true);
  return (
    <div>
      <InfoPanel label="Let's pin down your 'top schools' request"
        help="A few quick choices so the system ranks exactly the schools you mean." />
      <Radio id="metric" label="Rank schools by which measure?"
        value={metric} onChange={setMetric}
        options={[
          {value: 'combined', label: 'Overall SAT score (maths + reading + writing)'},
          {value: 'math', label: 'Average maths score'},
          {value: 'reading', label: 'Average reading score'},
          {value: 'takers', label: 'Number of pupils who sat the SAT'}
        ]} />
      <Dropdown id="region" label="Which part of California?"
        value={region} onChange={setRegion}
        options={[
          {value: 'all', label: 'All of California'},
          {value: 'Los Angeles', label: 'Los Angeles County'},
          {value: 'San Diego', label: 'San Diego County'},
          {value: 'Alameda', label: 'Alameda County'},
          {value: 'Orange', label: 'Orange County'}
        ]} />
      <NumberInput id="topN" label="How many schools should we return?"
        min={1} max={50} step={1} value={topN} onChange={setTopN} />
      <Toggle id="completeOnly" label="Only include schools with complete SAT results"
        value={completeOnly} onChange={setCompleteOnly} />
      <button className="primary" onClick={() =>
        submitResponses({metric, region, topN, completeOnly})}>
        Show me the answer
      </button>
    </div>
  );
}
""".strip()

_STUB_C3_FIELDS_SCHOOLS = [
    {"id": "metric", "label": "Which measure to rank schools by"},
    {"id": "region", "label": "Which part of California"},
    {"id": "topN", "label": "How many schools to return"},
    {"id": "completeOnly", "label": "Only schools with complete SAT results"},
]

_STUB_C3_JSX_FINANCIAL = """
function Interface() {
  const [period, setPeriod] = React.useState({start: '', end: ''});
  const [txnTypes, setTxnTypes] = React.useState(['credit']);
  const [minAmount, setMinAmount] = React.useState(1000);
  const [note, setNote] = React.useState('');
  return (
    <div>
      <InfoPanel label="Let's pin down the period and kind of activity"
        help="Tell the system which transactions to look at." />
      <DateRange id="period" label="Over what period?"
        value={period} onChange={setPeriod} />
      <Checkboxes id="txnTypes" label="Which kinds of transaction?"
        value={txnTypes} onChange={setTxnTypes}
        options={[
          {value: 'credit', label: 'Money in (credit)'},
          {value: 'withdrawal', label: 'Money out (withdrawal)'},
          {value: 'transfer', label: 'Transfers to other banks'}
        ]} />
      <Slider id="minAmount" label="Only include transactions at or above this amount"
        min={0} max={10000} step={100} value={minAmount} onChange={setMinAmount} />
      <TextInput id="note" label="Anything else to add? (optional)"
        value={note} onChange={setNote} />
      <button className="primary" onClick={() =>
        submitResponses({period, txnTypes, minAmount, note})}>
        Show me the answer
      </button>
    </div>
  );
}
""".strip()

_STUB_C3_FIELDS_FINANCIAL = [
    {"id": "period", "label": "The period to look at"},
    {"id": "txnTypes", "label": "Which kinds of transaction"},
    {"id": "minAmount", "label": "Minimum transaction amount"},
    {"id": "note", "label": "Anything else to add?"},
]


def _canned_c3_bespoke(context: dict[str, Any]) -> str:
    # Pick the interface that fits the database the question is about.
    if context.get("db_name") == "financial":
        payload = {"jsx": _STUB_C3_JSX_FINANCIAL, "fields": _STUB_C3_FIELDS_FINANCIAL}
    else:
        payload = {"jsx": _STUB_C3_JSX_SCHOOLS, "fields": _STUB_C3_FIELDS_SCHOOLS}
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
