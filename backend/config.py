"""Central configuration — the primary tuning surface for the apparatus.

Every tunable parameter lives here as a named constant with a comment. See the build
brief §7. Nothing in here should require reading other modules to understand.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Model / API -------------------------------------------------------------
# Eventual real call target. The harness ships stubbed (USE_STUB below), so this is
# only consulted once the researcher goes live. A newer Opus may have shipped since
# this was written — bump it then (see README "Going live").
MODEL_NAME = "claude-opus-4-7"
MODEL_MAX_TOKENS_DEFAULT = 4096
MODEL_MAX_TOKENS_INTERFACE_GEN = 8192  # interface generation can be long (JSX)
MODEL_TEMPERATURE = 1.0
API_RETRY_ATTEMPTS = 3
API_RETRY_BACKOFF_SECONDS = 2

# THE switch. True = every Anthropic call returns a canned, correctly-shaped payload
# (no API key needed). Flip to False and supply ANTHROPIC_API_KEY to go live.
USE_STUB = True

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Databases (BIRD) --------------------------------------------------------
# The .sqlite files are NOT committed; the researcher drops them here. See
# bird_data/README.md. Paths are relative to BIRD_DATA_ROOT.
BIRD_DATA_ROOT = os.getenv("BIRD_DATA_ROOT", "./bird_data")
DATABASES: dict[str, dict[str, str]] = {
    "california_schools": {"sqlite": "california_schools/california_schools.sqlite"},
    "financial": {"sqlite": "financial/financial.sqlite"},
}

# Which ambiguity class each database hosts. Order within each list is the "slot"
# index used by counterbalancing. The participant never sees these labels.
SCHEMA_CLASS_MAP: dict[str, list[str]] = {
    "california_schools": ["schema_reference", "superlative_metric"],
    "financial": ["value_reference", "temporal_window"],
}
# Four ambiguity classes across two databases = four authored questions/participant.
# Each question is run once, under one condition (two under C2, two under C3), so a
# participant completes four trials. All four classes sit INSIDE AmbiSQL's detection
# taxonomy, so the C2-vs-C3 contrast is purely interface affordance, not detection.

# --- Session behaviour -------------------------------------------------------
SHOW_RESULT_ROW_LIMIT = 50            # rows displayed; true row_count still logged
SQL_EXECUTION_TIMEOUT_SECONDS = 10
QUESTION_AUTHORING_MIN_CHARS = 15     # soft nudge threshold (never blocks)
LOADING_SCREEN_MIN_SECONDS = 2        # fixed loading screen masks C3's longer latency

SESSION_LOG_DIR = os.getenv("SESSION_LOG_DIR", "./session_logs")
LOG_PROMPTS_VERBATIM = True           # store the fully-interpolated prompt per call
PILOT_MODE = False

# --- Derived paths -----------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
CALLS_DIR = BACKEND_DIR / "calls"


def db_path(name: str) -> Path:
    """Absolute path to a configured database's .sqlite file."""
    if name not in DATABASES:
        raise KeyError(f"Unknown database {name!r}; known: {list(DATABASES)}")
    root = Path(BIRD_DATA_ROOT)
    if not root.is_absolute():
        root = PROJECT_ROOT / root
    return (root / DATABASES[name]["sqlite"]).resolve()


def session_log_dir() -> Path:
    d = Path(SESSION_LOG_DIR)
    if not d.is_absolute():
        d = PROJECT_ROOT / d
    d.mkdir(parents=True, exist_ok=True)
    return d
