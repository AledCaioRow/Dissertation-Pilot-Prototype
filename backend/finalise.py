"""Parse the finaliser reply and serialise clarifications.

The finaliser must reply in exactly the OUTPUT_CONTRACT format:

    EXPLANATION: ...
    CONFIDENCE: <int 0-100>
    SQL:
    <one SELECT statement, last thing in the response>

Parsing rule (from the spec): split on the ``SQL:`` line; everything after is the
query, the lines before carry EXPLANATION and CONFIDENCE.
"""

import re


class FinaliserFormatError(ValueError):
    """The model's reply did not conform to the OUTPUT_CONTRACT."""


def parse_finaliser(text: str):
    """Return (explanation, confidence, sql). Raise FinaliserFormatError if malformed."""
    if not text or not text.strip():
        raise FinaliserFormatError("Empty finaliser response.")

    # Split on the first line that is exactly 'SQL:' (allowing surrounding space).
    m = re.search(r"(?im)^[ \t]*SQL:[ \t]*$", text)
    if not m:
        # Fall back to an inline 'SQL:' marker if the model didn't isolate it.
        m = re.search(r"(?i)\bSQL:\s*", text)
        if not m:
            raise FinaliserFormatError("No 'SQL:' marker found in finaliser response.")
    head = text[: m.start()]
    sql = text[m.end():].strip()

    # Strip accidental markdown fences around the SQL.
    sql = re.sub(r"^```[a-zA-Z]*\s*", "", sql).strip()
    sql = re.sub(r"\s*```$", "", sql).strip()
    if not sql:
        raise FinaliserFormatError("No SQL statement after the 'SQL:' marker.")

    exp_match = re.search(r"(?is)EXPLANATION:\s*(.*?)\s*(?:CONFIDENCE:|$)", head)
    explanation = exp_match.group(1).strip() if exp_match else head.strip()

    conf_match = re.search(r"(?i)CONFIDENCE:\s*(\d{1,3})", head)
    confidence = None
    if conf_match:
        confidence = max(0, min(100, int(conf_match.group(1))))

    return explanation, confidence, sql


def serialise_clarifications(clarifications) -> str:
    """Serialise resolved answers the SAME way for every condition.

    Produces ``Asked: … -> Answered: …`` lines, skipped items marked, so all three
    conditions hand the finaliser equivalent content.

    Accepts either a pre-formatted string (used by C1, whose chat reply is already
    in the window) or a list of resolution dicts (C2/C3).
    """
    if clarifications is None:
        return "(no clarifications provided)"
    if isinstance(clarifications, str):
        return clarifications
    if isinstance(clarifications, dict):
        clarifications = clarifications.get("resolutions", [])

    lines = []
    for r in clarifications:
        phrase = r.get("phrase") or r.get("id") or "(item)"
        asked = r.get("clarificationQuestion") or phrase
        if r.get("skipped"):
            lines.append(f"Asked: {asked} -> Answered: (skipped)")
            continue
        custom = (r.get("custom") or "").strip()
        selected = r.get("selected")
        if custom:
            answer = custom
        elif selected is not None and selected != "":
            answer = _label_for(r, selected)
        else:
            answer = "(no answer)"
        lines.append(f"Asked: {asked} -> Answered: {answer}")
    return "\n".join(lines) if lines else "(no clarifications provided)"


def _label_for(resolution, selected):
    for opt in (resolution.get("optionsShown") or resolution.get("options") or []):
        if opt.get("value") == selected:
            return f"{opt.get('label')} ({selected})" if opt.get("label") != selected else selected
    return str(selected)
