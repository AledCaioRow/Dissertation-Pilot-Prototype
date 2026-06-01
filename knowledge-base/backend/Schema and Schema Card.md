---
tags: [backend]
---
# Schema and Schema Card

Loads a database's structure and renders the **text schema card** that grounds every model call.

**Code:** [`backend/schema/load_schema.py`](../../backend/schema/load_schema.py) ·
[`backend/schema/schema_card.py`](../../backend/schema/schema_card.py)

## How it works (plain English)
1. `load_schema(name)` opens the database **read-only** and reads its tables, columns, types and
   foreign keys into small typed objects.
2. If the real `.sqlite` file isn't there yet, it returns a clearly-flagged **placeholder** schema
   so the wizard still runs (the researcher drops the BIRD files in later).
3. `build_schema_card(schema)` turns that structure into a compact, readable text block —
   tables, columns, keys — which is the only grounding the model gets (no separate hints layer).
4. `qualified_columns(schema)` lists every `table.column`, used to feed the C3 ColumnPicker.

**Key points**
- Read-only always; the study never writes to the databases.
- Run `python -m backend.schema.load_schema` to print each card as a sanity check.

**Connected:** [[Build Context]] · [[Main API]] (`GET /schema/{name}`) · [[Run SQL]] · [[C3 Primitives]]
