"""Prompt blocks for the student_club study.

Every string here is reproduced VERBATIM from PROMPTS.md. The frozen
``{{DB_CONTEXT}}`` is loaded once from ``DB_CONTEXT.md`` (the exact bytes) and
injected identically into every model call, so no condition is better-informed.

Build rules that protect the comparison:
- Every condition's system prompt opens with the same context stack: ROLE + DATABASE.
- Temperature 0 on every call (enforced in llm.py).
- The DB_CONTEXT bytes are read once at import and never regenerated per call.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent

# The frozen prompt-context artifact, read ONCE as exact bytes and reused.
DB_CONTEXT = (_HERE / "DB_CONTEXT.md").read_text(encoding="utf-8")

# Default SQL dialect; change this single value if the backend DB ever changes.
SQL_DIALECT = "SQLite"

# --- Shared blocks -----------------------------------------------------------

ROLE = (
    "You are helping a person who does not know SQL get information out of the "
    "student_club database. They have written a question in plain English."
)

DATABASE = (
    "DATABASE: student_club (SQLite). The following is the only thing you know about it:\n\n"
    f"{DB_CONTEXT}"
)

OUTPUT_CONTRACT = f"""EXPLANATION: <one plain-English paragraph, 50 words or fewer, saying what the query returns and how it matches the question. No SQL jargon.>
CONFIDENCE: <a single integer 0-100, your rough confidence the query correctly answers the question>
SQL:
<one {SQL_DIALECT} SELECT statement that answers the question, as the very last thing in your response>

SQL rules:
- Exactly one statement, SELECT only. No INSERT/UPDATE/DELETE/CREATE/PRAGMA, no second statement, no comments, no markdown fences.
- Use only tables and columns from the schema; join on the foreign keys shown.
- Do not add LIMIT unless the question asks for a specific number; a preview is shown separately.
- Write nothing after the SQL."""

# --- First turns (differ by condition) ---------------------------------------

A1_CHATBOT = f"""{ROLE}

{DATABASE}

YOUR TASK
Find the parts of the person's question that are unclear or could be read more than one way and that would change the SQL query needed to answer it. Then reply in one short, plain-language message telling them what you understood and asking about anything still unclear.

OUTPUT
One plain-language message, with no technical or database terms. You do not write SQL here; after the person's single reply you will be asked for the query."""

A2_AMBIGUITY = f"""{ROLE}

{DATABASE}

YOUR TASK
Find the parts of the person's question that are unclear or could be read more than one way and that would change the SQL query needed to answer it. Then return them as structured data for an on-screen interface the person resolves themselves; if nothing is unclear, return no ambiguities and a short restatement of their question instead.

OUTPUT
Return JSON ONLY (no markdown fences), in exactly this shape, because it is loaded straight into the interface:

{{
  "originalQuestion": "<the person's question, unchanged>",
  "summary": "<one short plain-language restatement of what you understood, shown to the person to confirm>",
  "ambiguities": [
    {{
      "id": "<short snake_case id>",
      "phrase": "<the exact words from the question>",
      "type": "<one of: unclear_schema_reference, unclear_value_reference, missing_keyword, unclear_knowledge_source, insufficient_reasoning_context, conflicting_knowledge, ambiguous_temporal_spatial_scope>",
      "affordance": "<one of: choice, value, range, toggle, dateRange>",
      "clarificationQuestion": "<one short plain-English question>",
      "evidence": "<one short line naming the schema columns behind it>",
      "allowCustom": <true unless a free-text answer makes no sense>,

      // include EXACTLY ONE of these, matching "affordance":
      "options":   [ {{ "value": "<value>", "label": "<what the person sees>" }} ],  // choice or value
      "range":     {{ "min": <n>, "max": <n>, "step": <n>, "unit": "<text>" }},        // range
      "toggle":    {{ "onLabel": "<text>", "offLabel": "<text>" }},                    // toggle
      "dateRange": {{ "earliest": "<YYYY-MM-DD>", "latest": "<YYYY-MM-DD>" }}          // dateRange
    }}
  ]
}}

- "affordance" decides the control shown: a choice of column/measure -> choice; a specific stored value -> value; a date or time span -> dateRange; a yes/no query decision such as counting duplicates or capping results -> toggle; a numeric threshold -> range.
- Fill options, ranges and dates only from the sample data and value lists in the DATABASE block; never invent any.
- One object per ambiguous span; there may be several. If "ambiguities" is empty, still fill "summary"."""

A3_DYNAMIC = f"""{ROLE}

{DATABASE}

YOUR TASK
Find the parts of the person's question that are unclear or could be read more than one way and that would change the SQL query needed to answer it. Then return the source code of a small interface, tailored to this question, that lets the person resolve them.

OUTPUT (strict)
Return CODE ONLY — no prose, no markdown fences, no imports. Write one React function component named Clarifier that uses ONLY these injected globals:
- React (use hooks as React.useState, etc.)
- onResolve(resolutions): call ONCE when the person finishes. resolutions MUST be an array of {{id, phrase, selected, custom, skipped}} (selected = chosen value or null, custom = free text or "", skipped = boolean).
- logEvent(type, payload): call on EVERY interaction (a selection, a text change, a skip, a back, the final submit), with clear type strings like "select","custom_type","skip","submit". Anything not passed to logEvent is lost data.
Constraints:
- No import/require, no fetch/network, no access to window or document beyond the component, no looping timers.
- It runs in a fixed panel (the host gives its exact width and height): use 100% of the width, let content scroll inside the panel if it needs more height, and never set fixed widths or absolute positions larger than that panel.
- Build controls suited to each ambiguity using only values from the DATABASE block. Give a way to skip any item and one clear finish button that calls onResolve.
Begin your output with: function Clarifier() {{"""


def a3_user(question: str, ambiguities_json: str) -> str:
    """The C3 first-turn user message (A3)."""
    return (
        f"QUESTION: {question}\n"
        f"AMBIGUITIES TO RESOLVE (the same set the fixed interface uses): {ambiguities_json}"
    )


# --- Finaliser turn (identical for C1, C2, C3) -------------------------------

def finalise_turn(clarifications: str) -> str:
    """The finalise user turn appended to the condition's existing window."""
    return f"""The person has now resolved their question through the interface. Their answers:

{clarifications}

Set the earlier output format aside. Using everything in this conversation and these answers, write the final query that answers their original question, in EXACTLY this format and nothing else:

{OUTPUT_CONTRACT}"""


# Map condition code -> first-turn system prompt.
SYSTEM_BY_CONDITION = {
    "1": A1_CHATBOT,
    "2": A2_AMBIGUITY,
    "3": A3_DYNAMIC,
}
