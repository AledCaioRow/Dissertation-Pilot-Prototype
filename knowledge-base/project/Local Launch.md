---
tags: [project]
---
# Local Launch

How the study app runs: **locally and supervised**, on the researcher's laptop. The backend
(FastAPI) and frontend (Vite) run side by side; the participant uses the browser tab. There is no
public/online deployment.

## How it works (plain English)
1. **One step.** From the repo root run `start.bat` (Windows) or `./start.sh` (Mac/Linux).
2. First run only, the script sets up a Python virtualenv + installs `requirements.txt`, and runs
   `npm install` in `frontend/`.
3. It then starts the backend on `http://localhost:8000` and the frontend on
   `http://localhost:5173`, and Vite opens the browser automatically.
4. The Vite dev server proxies `/api/*` to the backend, so the frontend never hard-codes the origin.
5. **Manual fallback:** `python -m uvicorn backend.main:app --port 8000` and, separately,
   `npm --prefix frontend run dev`.

## Stub vs live
- It runs in **stub mode out of the box** — no API key needed — so you can click the whole wizard.
- **Page 0** of the wizard lets the operator pick *Stubbed* or *Live API* per session.
- To make live the default: copy `backend/.env.example` to `backend/.env`, set `USE_STUB=False`
  and `ANTHROPIC_API_KEY=…`. Live also needs the real call implemented (the `# TODO` in
  [[Stub Call Layer]]). The key lives only in `backend/.env`, never in the browser.

**Connected:** [[Stub vs Live]] · [[Config]] · [[Backend Overview]] · [[Frontend Overview]] · [[Production Cost and Ethics]] · [[Build Brief]]
