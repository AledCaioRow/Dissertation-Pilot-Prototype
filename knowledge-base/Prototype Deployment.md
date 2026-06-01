---
tags: [frontend, ops]
---
# Prototype Deployment

How the **▶ Open the prototype** link in the README is produced: a GitHub Actions workflow
builds the frontend and publishes it to GitHub Pages. The hosted build is frontend-only, so it
runs in demo/mock mode and the C3 condition shows the blank placeholder.

**Code:** [`.github/workflows/deploy-prototype.yml`](../.github/workflows/deploy-prototype.yml) ·
Vite `base: "./"` in [`frontend/vite.config.js`](../frontend/vite.config.js)

**Key points**
- Triggers on push to `main` and `claude/**`, plus manual dispatch; deploys with
  `configure-pages` (auto-enablement) + `deploy-pages`.
- URL: `https://aledcaiorow.github.io/My-first-Streamlit-app/` (changes if the repo is renamed).
- Mock mode is automatic because there's no backend at the Pages origin — see [[API Client and Mock]].

**Connected**
- [[Frontend Overview]] · [[Stub vs Live]] · README (`▶ Open the prototype`)
