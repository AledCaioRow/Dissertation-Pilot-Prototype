---
tags: [frontend]
---
# Copy

All participant-facing wording in one file, so changes are a one-file edit with no code change.
British English, deliberately jargon-free.

**Code:** [`frontend/src/content/copy.json`](../frontend/src/content/copy.json) ·
canonical spec [[page_copy]]

**Key points**
- Keyed strings/arrays for every screen; components read keys, never hard-code text.
- Authoring prompts keyed by `schema:class` to line up with `SCHEMA_CLASS_MAP` ([[Ambiguity Classes]]);
  the participant never sees the class label.
- Includes SUS (canonical Brooke 1996 wording — do not paraphrase) and the agency items.

**Connected**
- [[Screen Components]] (consumers) · [[Wizard App]] · [[page_copy]]
