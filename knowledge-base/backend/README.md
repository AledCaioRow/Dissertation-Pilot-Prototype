# backend/

The FastAPI server, organised by model call. Each code note has a plain-English "How it works"
walkthrough and a link to the real source file.

- [[Backend Overview]] — how the pieces fit; the by-call layout and loader.
- [[Config]] — the central tunables, the two databases, the default mode.
- [[Schema and Schema Card]] — load a DB's structure; render the grounding card.
- [[Run SQL]] — real, read-only, timeout-guarded local SQLite execution.
- [[Build Context]] — build the shared schema-card-+-question context once per trial.
- [[Stub Call Layer]] — the one model-call entry point; stub payloads + the live TODO.
- [[Call 1 Interface Generation]] — condition-specific first call (C2 widgets / C3 JSX).
- [[Call 2 Query Generation]] — shared: generate → execute → explain (no call 3).
- [[Conditions C1 C2 C3]] — thin orchestration per condition.
- [[Counterbalancing]] — deterministic id → assignment (2×C2 + 2×C3).
- [[Logging]] — one resumable JSON session log per participant.
- [[Main API]] — the endpoints, incl. page-0 `/session/mode`.
