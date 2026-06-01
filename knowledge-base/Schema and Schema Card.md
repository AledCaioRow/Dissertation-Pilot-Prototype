---
tags: [backend]
---
# Schema and Schema Card

Loads a database's structure (tables, columns, types, FKs) and renders the **text schema
card** that grounds every model call.

**Code:** [`backend/schema/load_schema.py`](../backend/schema/load_schema.py) ·
[`backend/schema/schema_card.py`](../backend/schema/schema_card.py)

**Key points**
- `load_schema(name)` reads the `.sqlite` read-only; if the file is absent it returns a
  clearly-flagged **placeholder** so the wizard still runs (see [[Stub vs Live]]).
- `build_schema_card()` → compact text used by [[Build Context]].
- `qualified_columns()` feeds the C3 [[C3 Primitives]] ColumnPicker.
- Sanity script: `python -m backend.schema.load_schema`.

**Connected**
- [[Build Context]] · [[Main API]] (`GET /schema/{name}`) · [[Run SQL]]
