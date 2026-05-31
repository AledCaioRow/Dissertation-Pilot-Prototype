"""C2 condition — the faithful AmbiSQL static clarifier (call 1).

Thin by design: call 2 is shared across conditions, so a condition module only owns its
call-1 step. See docs/spec/ambisql_static_interface.md.
"""
from __future__ import annotations

from backend.calls import load_call_module
from backend.context.build_context import Context

_handler = load_call_module("01_interface_generation", "handler")

CONDITION = "C2"


def run_interface(context: Context):
    """Run call 1 for C2 → (ClarificationData, CallLogRecord)."""
    return _handler.generate_interface_c2(context)
