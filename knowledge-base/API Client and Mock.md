---
tags: [frontend]
---
# API Client and Mock

The session API client, with a standalone fallback so the wizard runs with no backend.

**Code:** [`frontend/src/api.js`](../frontend/src/api.js) · [`frontend/src/mockApi.js`](../frontend/src/mockApi.js)

**Key points**
- `detectMode()` pings `/config` once at startup → `"real"` (hit FastAPI via the `/api` proxy)
  or `"mock"` (in-browser canned data). After that `api.*` routes automatically (a Proxy).
- `mockApi` mirrors the [[Main API]] contracts; **C3 returns the blank placeholder**
  (`{ jsx: "", placeholder: true }`) — the empty slot rendered by [[C3 Dynamic Host]].
- This is what makes the hosted, backend-free [[Prototype Deployment]] possible.

**Connected**
- [[Wizard App]] (calls these) · [[Main API]] (the real endpoints) · [[Stub vs Live]]
