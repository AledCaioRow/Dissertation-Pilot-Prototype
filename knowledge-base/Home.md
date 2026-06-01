---
tags: [moc, home]
---
# 🗂 HITL Text-to-SQL — Knowledge Base

Map of content for the whole apparatus. Open the **repo root** as an
[Obsidian](https://obsidian.md) vault, then open the **graph view** — every note below is
wiki-linked, so the specs, the backend, the frontend and the design concepts form one
connected graph. The wiki-links between notes are the graph's edges.

> New here? Read [[The Experiment C2 vs C3]] then [[One-shot Two-call Interaction]].

## Canonical specs (`docs/`)
- [[CLAUDE_CODE_BRIEF]] — the hub: architecture, structure, build order
- [[ambisql_static_interface]] — the C2 fixed interface (faithful AmbiSQL)
- [[dynamic_interface]] — the C3 bespoke host + the component primitive set
- [[model_prompts]] — the three model-call prompts
- [[page_copy]] — every word the participant reads

## Concepts
- [[The Experiment C2 vs C3]]
- [[One-shot Two-call Interaction]]
- [[Ambiguity Classes]]
- [[Overreliance Probe]]
- [[Stub vs Live]]

## Backend
- [[Backend Overview]]
- [[Config]] · [[Schema and Schema Card]] · [[Run SQL]] · [[Build Context]]
- [[Stub Call Layer]] · [[Call 1 Interface Generation]] · [[Call 2 Query Generation]]
- [[Conditions C1 C2 C3]] · [[Counterbalancing]] · [[Logging]] · [[Main API]]

## Frontend
- [[Frontend Overview]]
- [[Wizard App]] · [[API Client and Mock]] · [[Copy]] · [[Screen Components]]
- [[C2 Static Interface]] · [[C3 Dynamic Host]] · [[C3 Primitives]]

## Analysis & ops
- [[Analysis Notebook]]
- [[Prototype Deployment]]

---
*Every `.md` in this repo is a node: the three READMEs, the specs, these notes. Notes link
out to the real source files too, so the graph doubles as a code map.*
