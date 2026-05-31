# BIRD databases (not committed)

The two SQLite databases the study uses are **not** in version control (this whole folder
is git-ignored except this README). Drop the BIRD files in at exactly these paths so they
match `DATABASES` in `backend/config.py`:

```
bird_data/california_schools/california_schools.sqlite
bird_data/financial/financial.sqlite
```

Both are standard databases from the **BIRD** Text-to-SQL benchmark
(https://bird-bench.github.io/). Until they are present, the app still runs end to end:
`backend/schema/load_schema.py` falls back to a small **placeholder** schema (clearly
flagged) so authoring screens render, and SQL execution returns a neutral error which the
wizard handles gracefully.

Open is **read-only** (`mode=ro`) — the apparatus never writes to these files.
