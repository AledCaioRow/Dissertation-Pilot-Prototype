"""End-to-end smoke test for the student_club study backend.

Runs the whole pipeline in-process (FastAPI TestClient — no separate server),
exercising C1 + C2 + C3 + logging, then prints a PASS/FAIL row-count table for
every logging table and confirms events.jsonl grew. Fails loud if any table is
empty or any model call returned non-conforming output.

Requires ANTHROPIC_API_KEY (real model calls at temperature 0).

Usage:  python scripts/smoke_test.py
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(HERE / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    raise SystemExit("ANTHROPIC_API_KEY not set — cannot run the smoke test.")

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402
import store  # noqa: E402

QUESTIONS = [
    "Which were the club's most successful events recently?",
    "Who spent the most money on food?",
    "How many people usually come to our socials?",
]

failures = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        failures.append(name)


def main_flow(client):
    events_path = store.EVENTS_JSONL
    before = events_path.stat().st_size if events_path.exists() else 0

    # 1) start session
    r = client.post("/api/session/start", json={
        "demographics": {"age": "25-34", "exp": "None", "freq": "Rarely"},
        "user_agent": "smoke-test",
    })
    check("session/start", r.status_code == 200, r.text)
    session_id = r.json()["session_id"]

    # 2) post three questions
    r = client.post("/api/questions", json={
        "session_id": session_id,
        "questions": [
            {"index": i, "text": q, "submitted_at": "2026-06-05T00:00:00Z"}
            for i, q in enumerate(QUESTIONS)
        ],
    })
    check("questions", r.status_code == 200 and r.json().get("ok"), r.text)

    # 3) C2 ambiguities for question 0
    r = client.post("/api/ambiguities", json={
        "session_id": session_id, "question_index": 0, "question": QUESTIONS[0],
    })
    check("ambiguities (A2)", r.status_code == 200, r.text)
    spec = r.json() if r.status_code == 200 else {}
    check("ambiguities shape",
          "originalQuestion" in spec and "summary" in spec and "ambiguities" in spec,
          str(list(spec.keys())))
    ambiguities = spec.get("ambiguities", [])

    # 4) finalise C2 for question 0
    resolutions = [
        {"id": a.get("id"), "phrase": a.get("phrase"),
         "clarificationQuestion": a.get("clarificationQuestion"),
         "selected": (a.get("options") or [{}])[0].get("value") if a.get("options") else None,
         "custom": "", "skipped": False,
         "optionsShown": a.get("options")}
        for a in ambiguities
    ]
    r = client.post("/api/finalize", json={
        "session_id": session_id, "question_index": 0,
        "condition": "2", "clarifications": resolutions,
    })
    check("finalize (C2)", r.status_code == 200, r.text)
    if r.status_code == 200:
        fr = r.json()
        check("finalize returns SQL + rows",
              bool(fr.get("sql")) and "total_count" in fr and "preview_rows" in fr,
              f"total={fr.get('total_count')}, confidence={fr.get('confidence')}")
        check("finalize SQL is SELECT",
              fr.get("sql", "").lstrip("(").lower().startswith(("select", "with")),
              fr.get("sql", "")[:60])

    # 5) C1 one chat turn for question 1
    r = client.post("/api/chat", json={
        "session_id": session_id, "question_index": 1,
        "history": [{"role": "user", "content": QUESTIONS[1]}],
    })
    check("chat (A1)", r.status_code == 200 and bool(r.json().get("reply")), r.text)

    # 6) C3 dynamic for question 2; check the source parses structurally
    r = client.post("/api/dynamic", json={
        "session_id": session_id, "question_index": 2, "question": QUESTIONS[2],
    })
    check("dynamic (A3)", r.status_code == 200, r.text)
    if r.status_code == 200:
        src = r.json().get("component_src", "")
        ok = src.startswith("function Clarifier()") and src.count("{") == src.count("}") \
            and src.count("(") == src.count(")")
        check("dynamic source parses (structural)", ok, src[:60])

    # 7) resolution log
    r = client.post("/api/resolution-log", json={
        "session_id": session_id, "question_index": 0,
        "log": {"originalQuestion": QUESTIONS[0], "resolutions": resolutions,
                "completedAt": "2026-06-05T00:00:00Z"},
    })
    check("resolution-log", r.status_code == 200, r.text)

    # 8) feedback
    r = client.post("/api/feedback", json={
        "session_id": session_id, "condition": "2", "question_index": 0,
        "q1": 3, "q2": 4, "text": "smoke test feedback",
    })
    check("feedback", r.status_code == 200, r.text)

    # 9) a handful of events
    r = client.post("/api/log", json={"events": [
        {"session_id": session_id, "screen": "welcome", "event_type": "screen_enter",
         "ts_client": "2026-06-05T00:00:00Z"},
        {"session_id": session_id, "screen": "task", "event_type": "question_submit",
         "question_index": 0, "value_json": {"text": QUESTIONS[0]},
         "ts_client": "2026-06-05T00:00:01Z"},
        {"session_id": session_id, "screen": "interface-2", "condition": "2",
         "event_type": "wizard_option_select", "target_id": "amb_successful",
         "ts_client": "2026-06-05T00:00:02Z"},
    ]})
    check("log events", r.status_code == 200 and r.json().get("written") == 3, r.text)

    client.post("/api/session/end", json={"session_id": session_id})

    # 10) row-count table
    print("\n--- logging table row counts ---")
    counts = store.table_counts()
    for t, n in counts.items():
        check(f"table {t} non-empty", n > 0, f"{n} rows")

    after = events_path.stat().st_size if events_path.exists() else 0
    check("events.jsonl grew", after > before, f"{before} -> {after} bytes")


if __name__ == "__main__":
    with TestClient(main.app) as client:
        main_flow(client)
    print()
    if failures:
        print(f"SMOKE TEST FAILED — {len(failures)} check(s): {failures}")
        sys.exit(1)
    print("SMOKE TEST PASSED — C1 + C2 + C3 + logging all green.")
