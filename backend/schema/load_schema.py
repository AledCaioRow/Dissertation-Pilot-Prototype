"""Load a database's structure (tables, columns, types, foreign keys).

Used two ways: the `/schema/{name}` endpoint serialises a `Schema` to JSON for the
bland `SchemaCard`, and `schema_card.py` renders it to the text card injected into
every model call.

If the real .sqlite is absent (the researcher has not dropped the BIRD files in yet),
we return a small, clearly-flagged *placeholder* so the wizard still runs end to end.
Real data overrides the placeholder automatically once the file is present.

Run directly as a sanity check (build order step 2):  python -m backend.schema.load_schema
"""
from __future__ import annotations

import sqlite3
from typing import Optional

from pydantic import BaseModel

from backend import config


class Column(BaseModel):
    name: str
    type: str
    notnull: bool = False
    pk: bool = False


class ForeignKey(BaseModel):
    column: str
    ref_table: str
    ref_column: str


class Table(BaseModel):
    name: str
    columns: list[Column]
    foreign_keys: list[ForeignKey] = []


class Schema(BaseModel):
    name: str
    tables: list[Table]
    placeholder: bool = False  # True if the real .sqlite was not found


def _load_from_sqlite(name: str) -> Schema:
    path = config.db_path(name)
    # Read-only open via URI so we never mutate the participant's data.
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        table_names = [r[0] for r in cur.fetchall()]
        tables: list[Table] = []
        for tname in table_names:
            cols = [
                Column(
                    name=r["name"],
                    type=(r["type"] or "").upper() or "TEXT",
                    notnull=bool(r["notnull"]),
                    pk=bool(r["pk"]),
                )
                for r in cur.execute(f'PRAGMA table_info("{tname}")').fetchall()
            ]
            fks = [
                ForeignKey(column=r["from"], ref_table=r["table"], ref_column=r["to"])
                for r in cur.execute(f'PRAGMA foreign_key_list("{tname}")').fetchall()
            ]
            tables.append(Table(name=tname, columns=cols, foreign_keys=fks))
        return Schema(name=name, tables=tables, placeholder=False)
    finally:
        conn.close()


def load_schema(name: str, *, allow_placeholder: bool = True) -> Schema:
    """Load a configured schema. Falls back to a placeholder if the file is missing."""
    if name not in config.DATABASES:
        raise KeyError(f"Unknown database {name!r}; known: {list(config.DATABASES)}")
    try:
        return _load_from_sqlite(name)
    except sqlite3.OperationalError as exc:
        if not allow_placeholder:
            raise FileNotFoundError(
                f"Could not open {config.db_path(name)} read-only: {exc}. "
                f"Drop the BIRD .sqlite file in (see bird_data/README.md)."
            ) from exc
        print(
            f"[schema] WARNING: {config.db_path(name)} not found; using placeholder "
            f"schema for {name!r}. Drop the real BIRD file in to use live data."
        )
        return _PLACEHOLDERS[name].model_copy(deep=True)


# --- Placeholder schemas (trimmed, representative of the BIRD originals) -------
# Only used when the real .sqlite is absent, so the wizard, stub and schema card
# all have something sensible to show before the databases are populated.
_PLACEHOLDERS: dict[str, Schema] = {
    "california_schools": Schema(
        name="california_schools",
        placeholder=True,
        tables=[
            Table(
                name="schools",
                columns=[
                    Column(name="CDSCode", type="TEXT", pk=True),
                    Column(name="School", type="TEXT"),
                    Column(name="District", type="TEXT"),
                    Column(name="County", type="TEXT"),
                    Column(name="City", type="TEXT"),
                    Column(name="StatusType", type="TEXT"),
                ],
            ),
            Table(
                name="satscores",
                columns=[
                    Column(name="cds", type="TEXT", pk=True),
                    Column(name="sname", type="TEXT"),
                    Column(name="NumTstTakr", type="INTEGER"),
                    Column(name="AvgScrRead", type="INTEGER"),
                    Column(name="AvgScrMath", type="INTEGER"),
                    Column(name="AvgScrWrite", type="INTEGER"),
                ],
                foreign_keys=[ForeignKey(column="cds", ref_table="schools", ref_column="CDSCode")],
            ),
            Table(
                name="frpm",
                columns=[
                    Column(name="CDSCode", type="TEXT", pk=True),
                    Column(name="Academic Year", type="TEXT"),
                    Column(name="Enrollment (K-12)", type="REAL"),
                    Column(name="Free Meal Count (K-12)", type="REAL"),
                    Column(name="FRPM Count (K-12)", type="REAL"),
                ],
                foreign_keys=[ForeignKey(column="CDSCode", ref_table="schools", ref_column="CDSCode")],
            ),
        ],
    ),
    "financial": Schema(
        name="financial",
        placeholder=True,
        tables=[
            Table(
                name="district",
                columns=[
                    Column(name="district_id", type="INTEGER", pk=True),
                    Column(name="A2", type="TEXT"),  # district name
                    Column(name="A3", type="TEXT"),  # region
                ],
            ),
            Table(
                name="account",
                columns=[
                    Column(name="account_id", type="INTEGER", pk=True),
                    Column(name="district_id", type="INTEGER"),
                    Column(name="frequency", type="TEXT"),
                    Column(name="date", type="DATE"),
                ],
                foreign_keys=[ForeignKey(column="district_id", ref_table="district", ref_column="district_id")],
            ),
            Table(
                name="client",
                columns=[
                    Column(name="client_id", type="INTEGER", pk=True),
                    Column(name="gender", type="TEXT"),
                    Column(name="birth_date", type="DATE"),
                    Column(name="district_id", type="INTEGER"),
                ],
                foreign_keys=[ForeignKey(column="district_id", ref_table="district", ref_column="district_id")],
            ),
            Table(
                name="trans",
                columns=[
                    Column(name="trans_id", type="INTEGER", pk=True),
                    Column(name="account_id", type="INTEGER"),
                    Column(name="date", type="DATE"),
                    Column(name="type", type="TEXT"),
                    Column(name="operation", type="TEXT"),
                    Column(name="amount", type="INTEGER"),
                    Column(name="balance", type="INTEGER"),
                    Column(name="k_symbol", type="TEXT"),
                ],
                foreign_keys=[ForeignKey(column="account_id", ref_table="account", ref_column="account_id")],
            ),
            Table(
                name="loan",
                columns=[
                    Column(name="loan_id", type="INTEGER", pk=True),
                    Column(name="account_id", type="INTEGER"),
                    Column(name="date", type="DATE"),
                    Column(name="amount", type="INTEGER"),
                    Column(name="duration", type="INTEGER"),
                    Column(name="status", type="TEXT"),
                ],
                foreign_keys=[ForeignKey(column="account_id", ref_table="account", ref_column="account_id")],
            ),
        ],
    ),
}


if __name__ == "__main__":  # sanity script
    from backend.schema.schema_card import build_schema_card

    for db in config.DATABASES:
        schema = load_schema(db)
        flag = " (placeholder)" if schema.placeholder else ""
        print(f"\n===== {db}{flag} =====")
        print(build_schema_card(schema))
