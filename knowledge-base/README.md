# Knowledge base — read me first

This folder is a self-contained **Obsidian vault** documenting the whole project: the concepts
behind the study, every backend and frontend module (in plain English), the analysis, how to run
it, and pointers to the canonical specs. It is a companion to the code, not the code itself.

## How to open it
1. Install [Obsidian](https://obsidian.md).
2. *Open folder as vault* → choose **this `knowledge-base/` folder**.
3. Every wiki-link resolves inside the vault (no dangling links), and **Graph view** shows how
   the notes connect. Spec documents in `docs/` appear as `specs/` notes that link out to the real files.

> Opening `knowledge-base/` as the vault is what keeps links working. (You *can* open the repo root
> instead, but then unrelated READMEs join the graph.)

## Where to start
**This file → [[Home]] → `concepts/` → the area folder you care about.**
- New to the project? Read `concepts/` then [[Design Overview]].
- Want to run it? [[Local Launch]].
- Reading the code? `backend/` and `frontend/` — each note has a "How it works (plain English)"
  walkthrough plus a link to the real source file.

## Folder map
| Folder | What's in it |
|---|---|
| `concepts/` | The *why*: the experiment, two-call interaction, ambiguity classes, overreliance, stub vs live. |
| `backend/` | The FastAPI server, one note per module, by model call. |
| `frontend/` | The React + Vite wizard, one note per module. |
| `analysis/` | The post-hoc analysis notebook. |
| `project/` | Running it, cost & ethics, and the design rationale. |
| `specs/` | In-vault pointers to the canonical specs in `docs/`. |

Each folder has its own `README.md` listing its notes; [[Home]] is the index/graph hub.

## Keeping it current (regenerator — stubbed)
The KB does **not** self-sync. After changing the code you can run a one-command **manual** refresh:

```
python scripts/regenerate_knowledge_base.py          # dry run: prints which sources map to which notes
python scripts/regenerate_knowledge_base.py --write   # would rewrite the code-area notes
```

The actual model pass is **stubbed** today — a documented `# TODO: replace stub with real Anthropic
call`, mirroring `backend/calls/_stub.py` — so the dry run prints the plan and changes nothing.
Concept/spec/project notes are hand-authored and not regenerated. Wiring this as a git pre-commit
hook is noted as future work (it would still be human-triggered and reviewed, not automatic).
