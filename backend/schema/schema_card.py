"""Render a `Schema` to the text "schema card" injected into every model call.

The card carries everything the model needs to ground itself — tables, columns,
types, and foreign keys — so there is no separate hints layer (build brief §3, §7).
Deliberately compact and readable.
"""
from __future__ import annotations

from backend.schema.load_schema import Schema, load_schema


def build_schema_card(schema: Schema) -> str:
    """A compact, model-readable description of the schema."""
    lines: list[str] = [f"Database: {schema.name}"]
    if schema.placeholder:
        lines.append("(NOTE: placeholder schema — real .sqlite not yet present.)")
    for table in schema.tables:
        col_parts = []
        for c in table.columns:
            tag = " PK" if c.pk else ""
            col_parts.append(f"{c.name} {c.type}{tag}")
        lines.append("")
        lines.append(f"Table {table.name}:")
        for part in col_parts:
            lines.append(f"  - {part}")
        for fk in table.foreign_keys:
            lines.append(
                f"  FK: {table.name}.{fk.column} -> {fk.ref_table}.{fk.ref_column}"
            )
    return "\n".join(lines)


def schema_card_for(name: str) -> str:
    """Convenience: load a configured database and render its card."""
    return build_schema_card(load_schema(name))


def qualified_columns(schema: Schema) -> list[str]:
    """All columns as `table.column`, for the C3 ColumnPicker primitive."""
    return [f"{t.name}.{c.name}" for t in schema.tables for c in t.columns]
