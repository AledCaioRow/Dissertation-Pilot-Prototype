"""Helpers shared across the model-call folders.

The call folders are named with a numeric prefix (`01_interface_generation`, …) so the
call structure is self-evident on disk — but those names are not valid Python module
identifiers, so we load their `io.py` / `handler.py` by file path and cache them.
Prompts are likewise loaded from their `.txt` files at runtime (editability: a prompt
change is a one-file edit, no code change).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from backend import config

_CALLS_DIR = Path(__file__).resolve().parent


def load_call_module(call_dir: str, module: str) -> Any:
    """Import e.g. load_call_module('01_interface_generation', 'handler').

    Cached under a synthetic dotted name so each module is executed once (so the
    pydantic classes inside have stable identity across importers).
    """
    synthetic = f"backend.calls._loaded_{call_dir}_{module}"
    if synthetic in sys.modules:
        return sys.modules[synthetic]
    path = _CALLS_DIR / call_dir / f"{module}.py"
    spec = importlib.util.spec_from_file_location(synthetic, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[synthetic] = mod
    spec.loader.exec_module(mod)
    return mod


def load_prompt(call_dir: str, filename: str) -> str:
    """Read a prompt template from its call folder."""
    return (_CALLS_DIR / call_dir / filename).read_text(encoding="utf-8")


def extract_json_block(text: str) -> str:
    """Strip any preamble: take from the first `{` to the matching last `}`."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in model output: {text[:200]!r}")
    return text[start : end + 1]


def primitives_block() -> str:
    """The C3 primitive list, injected into the C3 prompt so prompt and host never drift.

    Single source of truth is docs/spec/dynamic_interface.md §3; this mirrors that table.
    """
    return (
        "- Radio: choose one of N (value: string)\n"
        "- Checkboxes: choose any of N (value: array of strings)\n"
        "- Dropdown: choose one of N, long lists (value: string)\n"
        "- MultiSelect: choose several, long lists (value: array of strings)\n"
        "- NumberInput: an exact number (value: number)\n"
        "- Slider: a number in a range, e.g. a threshold/percentage (value: number)\n"
        "- DatePicker: a single date (value: ISO date string)\n"
        "- DateRange: a date window (value: {start, end} ISO strings)\n"
        "- Toggle: a binary choice, e.g. ALL vs ANY (value: boolean)\n"
        "- ColumnPicker: point at a column in the shown schema (value: qualified column)\n"
        "- TextInput: free text, use sparingly (value: string)\n"
        "- InfoPanel: display-only explanation, no value\n"
        "Each control accepts id, label and a short plain-language help string; range "
        "controls accept min/max/step; option controls accept an options array of "
        "{value, label, help?}. The component must be named `Interface` and call "
        "submitResponses({...}) exactly once on its own submit button."
    )
