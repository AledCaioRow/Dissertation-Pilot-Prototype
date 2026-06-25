"""Dump every logging table to CSV for pandas/R.

Reads from the same database the app uses: a local SQLite file by default, or
Postgres when DATABASE_URL is set (e.g. point it at your Render database's
external connection string to pull the data locally).

Usage:  python scripts/export_csv.py [out_dir]
Defaults to <STUDY_LOG_DIR>/csv .
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

import store  # noqa: E402


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else store.LOG_DIR / "csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    with store.engine.connect() as conn:
        for t in store.EXPORT_TABLES:
            result = conn.execute(text(f"SELECT * FROM {t}"))
            cols = list(result.keys())
            rows = result.fetchall()
            path = out_dir / f"{t}.csv"
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(cols)
                for r in rows:
                    writer.writerow(list(r))
            print(f"wrote {path}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
