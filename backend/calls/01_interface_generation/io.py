"""I/O contracts for call 1 (interface generation).

C2 emits `ClarificationData` (faithful AmbiSQL multiple-choice), C3 emits
`BespokeInterface` ({jsx, fields}). See docs/spec/ambisql_static_interface.md §4 and
docs/spec/dynamic_interface.md §1. Loaded via importlib (numbered folder), so keep this
module import-light.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

# --- C2: static clarification data -------------------------------------------

AmbiguityType = Literal[
    "unclear_schema_reference",
    "unclear_value_reference",
    "missing_sql_keywords",
    "unclear_knowledge_source",
    "insufficient_reasoning_context",
    "conflicting_knowledge",
    "ambiguous_temporal_spatial_scope",
]


class C2Option(BaseModel):
    value: str
    label: str
    snippet: Optional[str] = None


class C2Widget(BaseModel):
    id: str
    ambiguity_type: AmbiguityType
    title: str
    description: Optional[str] = None
    options: list[C2Option]


class ClarificationData(BaseModel):
    """The C2 call-1 output."""
    widgets: list[C2Widget]
    allow_additional_constraints: bool = True


# --- C3: bespoke interface ---------------------------------------------------


class C3Field(BaseModel):
    id: str
    label: str


class BespokeInterface(BaseModel):
    """The C3 call-1 output."""
    jsx: str
    fields: list[C3Field]
