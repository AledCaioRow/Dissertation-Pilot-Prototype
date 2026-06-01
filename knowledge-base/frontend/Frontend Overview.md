---
tags: [frontend, moc]
---
# Frontend Overview

React 18 + Vite, plain JSX (no TypeScript) so the C3 dynamic-eval path stays simple. One
stylesheet, no CSS framework. The participant wizard, served locally alongside the backend.

**Code:** [`frontend/src/`](../../frontend/src)

## How it works (plain English)
1. `main.jsx` mounts `App`, which is the whole wizard as a state machine.
2. On load it reads `/config` (for the default mode) and starts the session; if the backend isn't
   reachable it shows a "launch with start.bat/start.sh" message.
3. The session runs entirely against the **local backend** — there is no offline/mock mode and no
   hosting. Page 0 lets the researcher pick stub vs live for the session.

## Map
- Flow engine → [[Wizard App]] (`App.jsx`); server calls → [[API Client]]
- All copy → [[Copy]] (`content/copy.json`); per-screen UI → [[Screen Components]]
- The two interfaces → [[C2 Static Interface]] · [[C3 Dynamic Host]] (+ [[C3 Primitives]])

**Connected:** [[Backend Overview]] (the server) · [[The Experiment C2 vs C3]] · [[Local Launch]]
