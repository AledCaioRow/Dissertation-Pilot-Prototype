---
tags: [moc, home]
---
# 🗂 HITL Text-to-SQL — Knowledge Base

Index for the whole apparatus. Open **this `knowledge-base/` folder** as an
[Obsidian](https://obsidian.md) vault (see `README.md` at the vault root), then open **graph
view** — every note is wiki-linked, so the concepts, backend, frontend, analysis and specs form
one connected graph with no dangling links.

> New here? Read `README.md`, then `concepts/` → [[The Experiment C2 vs C3]] → [[Design Overview]].

## Concepts (`concepts/`)
- [[The Experiment C2 vs C3]] · [[One-shot Two-call Interaction]] · [[Ambiguity Classes]]
- [[Overreliance Probe]] · [[Stub vs Live]]

## Backend (`backend/`)
- [[Backend Overview]]
- [[Config]] · [[Schema and Schema Card]] · [[Run SQL]] · [[Build Context]]
- [[Stub Call Layer]] · [[Call 1 Interface Generation]] · [[Call 2 Query Generation]]
- [[Conditions C1 C2 C3]] · [[Counterbalancing]] · [[Logging]] · [[Main API]]

## Frontend (`frontend/`)
- [[Frontend Overview]]
- [[Wizard App]] · [[API Client]] · [[Copy]] · [[Screen Components]]
- [[C2 Static Interface]] · [[C3 Dynamic Host]] · [[C3 Primitives]]

## Analysis (`analysis/`)
- [[Analysis Notebook]]

## Project (`project/`)
- [[Local Launch]] · [[Production Cost and Ethics]] · [[Design Overview]]

## Specs (`specs/` → link out to `docs/`)
- [[Build Brief]] — the canonical hub (architecture, structure, build order)
- [[AmbiSQL Static Interface]] · [[Dynamic Interface]] · [[Model Prompts]] · [[Page Copy]]

---
*Each code note links out to the real source file, so the graph doubles as a code map. Keep it
current with `scripts/regenerate_knowledge_base.py` (manual, stubbed — see `README.md`).*
