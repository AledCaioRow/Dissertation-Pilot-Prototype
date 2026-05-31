"""C3 condition — the bespoke, model-generated interface (call 1).

Thin by design: call 2 is shared across conditions, so a condition module only owns its
call-1 step. See docs/spec/dynamic_interface.md.
"""
from __future__ import annotations

from backend.calls import load_call_module
from backend.context.build_context import Context

_handler = load_call_module("01_interface_generation", "handler")

CONDITION = "C3"


def run_interface(context: Context):
    """Run call 1 for C3 → (BespokeInterface, CallLogRecord)."""
    return _handler.generate_interface_c3(context)
