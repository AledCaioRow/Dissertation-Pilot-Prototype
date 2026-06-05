"""Dump every logging table to CSV for pandas/R.

Usage:  python scripts/export_csv.py [out_dir]
Defaults to ./logs/csv .
"""

import csv
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LOG_DB = HERE / "logs" / "study_logs.sqlite"

TABLES = [
    "sessions", "questions", "model_calls", "responses",
    "resolution_logs", "dynamic_ui", "feedback", "events",
]


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "logs" / "csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not LOG_DB.exists():
        raise SystemExit(f"No logging DB at {LOG_DB}")
    conn = sqlite3.connect(LOG_DB)
    conn.row_factory = sqlite3.Row
    for t in TABLES:
        rows = conn.execute(f"SELECT * FROM {t}").fetchall()
        path = out_dir / f"{t}.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            if rows:
                writer.writerow(rows[0].keys())
                for r in rows:
                    writer.writerow(list(r))
            else:
                # still emit a header row from the table's columns
                cols = [c[1] for c in conn.execute(f"PRAGMA table_info({t})")]
                writer.writerow(cols)
        print(f"wrote {path}  ({len(rows)} rows)")
    conn.close()


if __name__ == "__main__":
    main()
