"""Deterministic counterbalancing: participant_id -> Assignment.

Three crossed binary/permutation factors (build brief §9):
  - schema_order          — a permutation of the configured databases
  - condition_block_order — ["C2","C3"] or reversed (which condition's block runs first)
  - slot_pattern          — within each schema, which class-slot maps to C2 vs C3

The brief describes "permutation of three / 24 assignments", which assumed three schemas.
The shipped study configures TWO databases, so this computes the table data-driven from
config.DATABASES: 2 schemas -> 2x2x2 = 8 balanced assignments; add a third database and it
grows to 24 with no code change. The slot pattern is applied uniformly across schemas, so a
participant always gets exactly half C2 and half C3 questions (two and two here).

Run directly to print the whole assignment table:  python -m backend.counterbalance.assign
"""
from __future__ import annotations

import itertools
from math import prod

from pydantic import BaseModel

from backend import config


class AuthoringSlot(BaseModel):
    database: str          # the db_name this authored question targets
    ambiguity_class: str   # researcher-only label; never shown to the participant
    slot: int              # class index within the schema (0/1)
    condition: str         # "C2" | "C3"


class Assignment(BaseModel):
    participant_id: int
    index: int                       # participant_id % n_assignments
    n_assignments: int
    schema_order: list[str]
    condition_block_order: list[str]
    slot_pattern: int
    authoring_plan: list[AuthoringSlot]   # order the authoring screens appear
    slot_to_condition: dict[str, str]     # "schema:class" -> condition


def _n_assignments() -> int:
    perms = len(list(itertools.permutations(config.DATABASES)))
    return prod([perms, 2, 2])


def assign(participant_id: int) -> Assignment:
    db_names = list(config.DATABASES)
    schema_perms = list(itertools.permutations(db_names))
    n_perms = len(schema_perms)
    n = prod([n_perms, 2, 2])

    i = participant_id % n
    schema_idx = i % n_perms
    block_idx = (i // n_perms) % 2
    slot_idx = (i // (n_perms * 2)) % 2

    schema_order = list(schema_perms[schema_idx])
    block_order = ["C2", "C3"] if block_idx == 0 else ["C3", "C2"]
    slot_base = ["C2", "C3"] if slot_idx == 0 else ["C3", "C2"]

    authoring_plan: list[AuthoringSlot] = []
    slot_to_condition: dict[str, str] = {}
    for db_name in schema_order:
        for slot, cls in enumerate(config.SCHEMA_CLASS_MAP[db_name]):
            cond = slot_base[slot % len(slot_base)]
            authoring_plan.append(
                AuthoringSlot(database=db_name, ambiguity_class=cls, slot=slot, condition=cond)
            )
            slot_to_condition[f"{db_name}:{cls}"] = cond

    return Assignment(
        participant_id=participant_id,
        index=i,
        n_assignments=n,
        schema_order=schema_order,
        condition_block_order=block_order,
        slot_pattern=slot_idx,
        authoring_plan=authoring_plan,
        slot_to_condition=slot_to_condition,
    )


def describe(a: Assignment) -> str:
    """Human-readable summary for the start-of-session check / logs."""
    counts = {"C2": 0, "C3": 0}
    for s in a.authoring_plan:
        counts[s.condition] += 1
    lines = [
        f"Participant {a.participant_id} -> assignment {a.index}/{a.n_assignments}",
        f"  schema order:          {' , '.join(a.schema_order)}",
        f"  condition block order: {' then '.join(a.condition_block_order)}",
        f"  slot pattern:          {a.slot_pattern}",
        f"  questions:             {counts['C2']} x C2, {counts['C3']} x C3",
    ]
    for s in a.authoring_plan:
        lines.append(f"    - {s.database} / {s.ambiguity_class} -> {s.condition}")
    return "\n".join(lines)


def all_assignments() -> list[Assignment]:
    """Every distinct assignment (for the analysis notebook's counterbalance table)."""
    return [assign(p) for p in range(_n_assignments())]


if __name__ == "__main__":
    for a in all_assignments():
        print(describe(a))
        print()
