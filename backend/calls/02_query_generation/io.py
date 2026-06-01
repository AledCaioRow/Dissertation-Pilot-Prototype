"""I/O contract for call 2 (query generation + post-execution explanation).

A single JSON object {interpretation, sql, explanation}; see
docs/prompts/model_prompts.md (call 2). Also holds `clean_sql`, the prose-stripping
fallback from build brief §11 (first ```sql block, else first SELECT/WITH).
"""
from __future__ import annotations

import re

from pydantic import BaseModel


class QueryGenerationResult(BaseModel):
    interpretation: str
    sql: str
    explanation: str = ""


_SQL_FENCE = re.compile(r"```sql\s*(.+?)```", re.IGNORECASE | re.DOTALL)
_SQL_START = re.compile(r"\b(SELECT|WITH)\b", re.IGNORECASE)


def clean_sql(raw: str) -> str:
    """If the model wrapped SQL in prose, recover the query (build brief §11)."""
    if not raw:
        return raw
    fence = _SQL_FENCE.search(raw)
    if fence:
        return fence.group(1).strip().rstrip(";").strip() + ";"
    m = _SQL_START.search(raw)
    if m:
        return raw[m.start():].strip()
    return raw.strip()
