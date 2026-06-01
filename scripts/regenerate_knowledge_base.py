#!/usr/bin/env python3
"""Regenerate the Obsidian knowledge base from the current codebase — STUBBED.

The knowledge base does NOT keep itself in sync on its own. This is a one-command, **manual**
refresh you run after changing the code, to re-derive the code-area notes from source. The
actual model pass is stubbed — a documented ``# TODO: replace stub with real Anthropic call``,
exactly like ``backend/calls/_stub.py``. Today it prints the regeneration *plan* (which source
files map to which notes) and changes nothing.

Usage:
    python scripts/regenerate_knowledge_base.py            # dry run: print the plan
    python scripts/regenerate_knowledge_base.py --write    # would rewrite notes (needs the model)

Future automation (not built): register this as a git pre-commit hook so the KB is offered a
refresh before each commit. It still would not be "automatic" — a human triggers and reviews it.
"""
from __future__ import annotations

import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge-base"

# Mirror the project's stubbed-call convention: the model call is disabled here.
USE_STUB = True

# Code-area notes -> the source file(s) each one documents. Concept/spec/project notes are
# hand-authored narrative and are intentionally NOT regenerated from source.
NOTE_SOURCES: dict[str, list[str]] = {
    "backend/Backend Overview.md": ["backend/main.py", "backend/calls/__init__.py"],
    "backend/Config.md": ["backend/config.py"],
    "backend/Schema and Schema Card.md": ["backend/schema/load_schema.py", "backend/schema/schema_card.py"],
    "backend/Run SQL.md": ["backend/execution/run_sql.py"],
    "backend/Build Context.md": ["backend/context/build_context.py"],
    "backend/Stub Call Layer.md": ["backend/calls/_stub.py"],
    "backend/Call 1 Interface Generation.md": [
        "backend/calls/01_interface_generation/handler.py",
        "backend/calls/01_interface_generation/io.py",
    ],
    "backend/Call 2 Query Generation.md": [
        "backend/calls/02_query_generation/handler.py",
        "backend/calls/02_query_generation/io.py",
    ],
    "backend/Conditions C1 C2 C3.md": [
        "backend/conditions/c1_baseline.py",
        "backend/conditions/c2_static.py",
        "backend/conditions/c3_bespoke.py",
    ],
    "backend/Counterbalancing.md": ["backend/counterbalance/assign.py"],
    "backend/Logging.md": ["backend/logging_io/session_log.py", "backend/logging_io/call_log.py"],
    "backend/Main API.md": ["backend/main.py"],
    "frontend/Frontend Overview.md": ["frontend/src/main.jsx", "frontend/src/styles.css"],
    "frontend/Wizard App.md": ["frontend/src/App.jsx"],
    "frontend/API Client.md": ["frontend/src/api.js"],
    "frontend/C2 Static Interface.md": ["frontend/src/components/C2StaticInterface.jsx"],
    "frontend/C3 Dynamic Host.md": ["frontend/src/components/C3DynamicHost.jsx"],
    "frontend/C3 Primitives.md": ["frontend/src/components/c3primitives.jsx"],
    "frontend/Copy.md": ["frontend/src/content/copy.json"],
    "frontend/Screen Components.md": ["frontend/src/components"],
    "analysis/Analysis Notebook.md": ["analysis/analysis.ipynb"],
}


def regenerate_note(note_rel: str, sources: list[str]) -> str | None:
    """Re-derive one note's body from its source files. STUBBED."""
    _ = "\n\n".join(
        (ROOT / s).read_text(encoding="utf-8")
        for s in sources
        if (ROOT / s).is_file()
    )
    if USE_STUB:
        # TODO: replace stub with real Anthropic call — summarise the source into the note body:
        # YAML tags, a plain-English "How it works" pseudocode walkthrough, wiki-links to related
        # notes, and a relative link to the source file. Until then, nothing is written.
        return None
    raise NotImplementedError("Live regeneration is not implemented yet (see the TODO above).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="rewrite notes (currently a no-op: model stubbed)")
    args = ap.parse_args()

    print(f"Knowledge base: {KB}")
    print(f"Mode: {'WRITE' if args.write else 'DRY RUN'} — the model pass is STUBBED (# TODO), so no files change.\n")

    missing = 0
    for note, sources in NOTE_SOURCES.items():
        present = [s for s in sources if (ROOT / s).exists()]
        absent = [s for s in sources if not (ROOT / s).exists()]
        flag = "" if not absent else f"   (MISSING: {', '.join(absent)})"
        print(f"  {note:42s} <- {', '.join(present) or '(none)'}{flag}")
        if args.write:
            regenerate_note(note, sources)  # no-op while stubbed
        missing += len(absent)

    print(f"\n{len(NOTE_SOURCES)} code-area notes mapped. Concept/spec/project notes are hand-authored.")
    print("The actual rewrite is a documented TODO (stubbed model call); no files were changed.")
    if missing:
        print(f"warning: {missing} source path(s) not found — the mapping may be out of date.")


if __name__ == "__main__":
    main()
