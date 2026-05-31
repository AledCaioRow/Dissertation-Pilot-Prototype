"""The shared context block, built once and reused by every condition.

Holding this constant across C1/C2/C3 is what isolates the experimental variable: the
only per-condition difference is the call-1 instruction, never the grounding context.
The schema card carries the real tables/columns/types/FKs, so there is no separate hints
layer (build brief §3).
"""
from __future__ import annotations

from pydantic import BaseModel

from backend.schema.schema_card import schema_card_for


class Context(BaseModel):
    db_name: str
    question: str
    schema_card: str

    def as_dict(self) -> dict:
        return {"db_name": self.db_name, "question": self.question, "schema_card": self.schema_card}


def build_context(db_name: str, question: str) -> Context:
    """Build the shared schema-card + question context for a trial."""
    return Context(
        db_name=db_name,
        question=question,
        schema_card=schema_card_for(db_name),
    )


def format_clarifications(responses: list[dict]) -> str:
    """Render the shared responses contract as `- <label>: <value>` lines for call 2."""
    if not responses:
        return "(no clarifications were collected)"
    lines = []
    for r in responses:
        label = r.get("label", r.get("field_id", "?"))
        value = r.get("value", "")
        if isinstance(value, dict):  # e.g. a date range {start, end}
            value = ", ".join(f"{k}: {v}" for k, v in value.items())
        elif isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)
