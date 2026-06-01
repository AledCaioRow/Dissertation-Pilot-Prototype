# Windows wrapper for the knowledge-base regenerator (see regenerate_knowledge_base.py).
# Manual, triggered refresh — the model pass is stubbed (# TODO).
$ErrorActionPreference = "Stop"
Set-Location -Path (Join-Path $PSScriptRoot "..")
python scripts/regenerate_knowledge_base.py @args
