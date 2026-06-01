---
tags: [frontend]
---
# API Client

The session API client. The study runs locally, so every call hits the backend through Vite's
`/api` proxy. (There is no offline mock — that belonged to the retired hosted demo.)

**Code:** [`frontend/src/api.js`](../../frontend/src/api.js)

## How it works (plain English)
1. Two helpers, `get`/`post`, call `'/api' + path`; non-2xx responses throw with the body text.
2. `api` exposes one method per backend endpoint: `getConfig`, `startSession`, **`setMode`** (page 0),
   `consent`, `screening`, `getSchema`, `author`, `trialInterface`, `trialAnswer`, `perceived`,
   `questionnaire`, `debrief`, `withdraw`.
3. Vite's dev server proxies `/api/*` to `http://localhost:8000`, so the frontend code never hard-codes
   the backend origin.

**Connected:** [[Wizard App]] (calls these) · [[Main API]] (the real endpoints) · [[Stub vs Live]]
