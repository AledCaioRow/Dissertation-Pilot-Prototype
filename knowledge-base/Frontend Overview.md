---
tags: [frontend, moc]
---
# Frontend Overview

React 18 + Vite, plain JSX (no TypeScript) so the C3 dynamic-eval path stays simple. One
stylesheet, no CSS framework. The participant wizard.

**Code:** [`frontend/src/`](../frontend/src)

**Map**
- Flow engine → [[Wizard App]] (`App.jsx`)
- Server calls (+ standalone mock) → [[API Client and Mock]]
- All copy → [[Copy]] (`content/copy.json`)
- Per-screen UI → [[Screen Components]]
- The two interfaces → [[C2 Static Interface]] · [[C3 Dynamic Host]] (+ [[C3 Primitives]])

**Key points**
- Runs two ways: with the backend, or standalone in demo/mock mode — see [[API Client and Mock]]
  and [[Prototype Deployment]].
- Styling is deliberately bland; British English throughout ([[page_copy]]).

**Connected**
- [[Backend Overview]] (the server) · [[The Experiment C2 vs C3]]
