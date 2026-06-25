# Putting the study online (plain-English guide)

This guide turns the study into a **website with one link** you can send to
participants, so nobody has to install anything or run commands. No technical
knowledge is needed — just follow the steps.

You'll deploy to **Render**, which builds the app straight from GitHub. The
project already contains everything Render needs (a `Dockerfile` and a
`render.yaml`), so you mostly just click buttons. Render will create **two**
things for you:

1. the **website** (the study itself), and
2. a **database** that safely stores everything participants do.

---

## What you'll end up with

* A single web address like `https://student-club-study.onrender.com`.
* Opening it shows the study exactly as it looks locally.
* Everything participants do is saved in a proper database — it survives app
  updates and restarts.
* You can download all collected data as spreadsheets from your browser whenever
  you like.

---

## Before you start — 3 things you need

1. **The code on GitHub** — done. It's on the `online-version` branch of your
   repository.
2. **An Anthropic API key** — this is what powers the model. Get one at
   <https://console.anthropic.com> → *API Keys*. It looks like `sk-ant-...`.
   Treat it like a password.
3. **A Render account** — free to create at <https://render.com>. Sign up with
   your GitHub account so Render can see your repository.

---

## What this costs: £0 for now

`render.yaml` is set to Render's **free** plans, so deploying costs **nothing**.
That's ideal for building it and testing. Two things to know about Free:

| Piece | On Free | What that means |
| --- | --- | --- |
| **Website** | sleeps when idle | After ~15 min with no visitors it sleeps; the next visit takes ~30–60s to wake, then it's normal. |
| **Database** | **deleted after ~30 days** | Render removes a free database about 30 days after you create it. **Before then**, either upgrade it (keeps your data) or export your data — otherwise it's lost. |

For **real participant sessions** later, upgrade to the small paid plans
(~$13/month total) so the site stays awake and your data is kept safely — see
**[Upgrade to the paid version](#upgrade-to-the-paid-version)** below. It's a
2-minute change and you only pay while you're collecting data.

---

## Step-by-step: deploy on Render

1. Go to <https://dashboard.render.com> and log in.
2. Click **New +** (top right) → **Blueprint**.
3. Choose your repository (`Dissertation-Pilot-Prototype`). If you don't see it,
   click *Configure account* and give Render access to the repo.
4. When asked for the **branch**, choose **`online-version`**.
5. Render reads `render.yaml` and shows **two resources**:
   * `student-club-study` (the website), and
   * `student-club-study-db` (the database).

   Click **Apply** / **Create**.
6. Render will ask you to fill in the secret value it needs:
   * **ANTHROPIC_API_KEY** → paste your `sk-ant-...` key.
   (You don't need to touch the others — `ADMIN_TOKEN` is generated for you, and
   the database connection is wired up automatically.)
7. Click **Apply** / **Deploy** and wait. The first build takes about
   **5–10 minutes** (it builds the app and creates the database). You're done
   when the website shows **"Live"**.

That's it — Render shows your web address near the top of the service page.

---

## Check it works

1. Click your new web address (e.g. `https://student-club-study.onrender.com`).
   You should see the study's first screen.
2. Add `/api/health` to the end of the address. You should see:

   ```json
   {"ok": true, "model": "claude-sonnet-4-6", "database": "connected"}
   ```

   `"database": "connected"` confirms the website can reach the database.
3. Do one full run-through yourself as a test participant, then download the
   data (next section) to confirm it was saved.

> If a model step shows an error, the most likely cause is the API key. Go to
> the website's **Environment** tab, check `ANTHROPIC_API_KEY` is correct, and
> that your Anthropic account has credit.

---

## Give it to participants

Just send them the web address. Nothing to install. Each person who opens it
gets their own session, and their answers are saved automatically to the
database.

---

## Get your data back out (as spreadsheets)

1. Find your secret download token: in Render, open the **website** service →
   **Environment** tab → copy the value of **`ADMIN_TOKEN`**.
2. In your browser, go to:

   ```
   https://YOUR-APP.onrender.com/api/admin/export?token=PASTE_THE_TOKEN_HERE
   ```

   This downloads **`study_export.zip`**. Inside are CSV spreadsheets — one per
   table (`sessions.csv`, `questions.csv`, `responses.csv`, `events.csv`, …).
3. Open the CSVs in **Excel, Google Sheets, R, Python, SPSS, or Power BI**.

> Keep your `ADMIN_TOKEN` private — anyone who has it can download the data.
> If it ever leaks, change it in Render's Environment tab (the app redeploys and
> the old token stops working). If you remove the token entirely, the download
> link is switched off (returns "Not found").

---

## Back up your data (recommended routine)

Render's managed Postgres also keeps its own backups on paid plans, but it's
good practice to keep your own copies:

1. Use the browser export (above) after every testing batch.
2. Save each download in a dated folder, e.g.

   ```text
   study_exports/
     2026-06-25_pilot_1_to_5/study_export.zip
     2026-06-30_main_batch_1/study_export.zip
   ```
3. Keep one copy locally and one in cloud storage.
4. **Always export before** deleting or changing anything in Render.

---

## Updating the study later

Any time you push a change to the `online-version` branch on GitHub, Render
rebuilds and redeploys the website automatically. Your data stays in the
database — updates don't touch it. You don't have to repeat the setup.

---

## Upgrade to the paid version

When you're ready for real participants — no sleeping, and your data kept beyond
30 days — upgrade the two pieces. **Do the database first**, and do it **before
the free database's ~30-day expiry** so nothing is lost. Upgrading keeps the same
database and all its data; nothing is wiped.

Easiest way (no files to edit):

1. **Database → paid.** Render dashboard → open **`student-club-study-db`** →
   **Settings** (look for the plan / *Upgrade* button) → pick a **Basic** plan
   (Basic-256MB, ~$6/mo, is plenty) → confirm. Your data stays.
2. **Website → no sleeping.** Render dashboard → open the **`student-club-study`**
   web service → **Settings** → **Instance Type / Plan** → change **Free** to
   **Starter** (~$7/mo) → confirm. It redeploys and stops sleeping.

That's about **~$13/month** total, only while you're collecting data — you can
downgrade or delete afterwards (export your data first).

> Prefer to keep the setting in the project? Change the two `plan:` lines in
> `render.yaml` — `free` → `starter` for the website, and `free` → `basic-256mb`
> for the database — then push. Render redeploys on the paid plans. Or just ask
> me and I'll make that change for you.

---

## Troubleshooting

| Symptom | Likely fix |
| --- | --- |
| Build fails immediately | Make sure you selected the **`online-version`** branch in the Blueprint step. |
| `/api/health` shows `"database": "disconnected"` | The database isn't reachable. Check both resources deployed, and that `DATABASE_URL` is present in the website's Environment tab (Render sets it automatically). |
| Page loads but model steps error | Check `ANTHROPIC_API_KEY` in the Environment tab and that your Anthropic account has credit. |
| First visit is very slow | On the **Free** website plan the site sleeps when idle and takes ~30–60s to wake. Starter stays awake. |
| `/api/admin/export` says "Not found" | `ADMIN_TOKEN` isn't set. Add one in the website's Environment tab (the blueprint generates one automatically). |
| Render rejects the database plan name | Plan names change occasionally. Pick any **Basic** Postgres plan from the dropdown in the dashboard. |

---

## For the technically curious (optional)

* **One service, one origin.** A multi-stage `Dockerfile` builds the React app
  (`frontend/`) and copies it next to the FastAPI backend, which serves the UI
  and the `/api/*` routes together. No CORS, one URL.
* **Same-origin frontend.** `frontend/.env.production` sets `VITE_API_BASE=""`,
  so the built app calls `/api` on its own host.
* **Data store.** Participant logging (`backend/store.py`) uses SQLAlchemy and
  reads `DATABASE_URL`: Postgres in the deployed version, or a local SQLite file
  when unset (so local dev needs no database). The same SQL runs on both. The
  read-only *content* database (`content_db.py`) stays SQLite — it ships with the
  app and is never written to.
* **Export anywhere.** `/api/admin/export` streams a zip of CSVs straight from
  the database, so it works the same on SQLite or Postgres. `scripts/export_csv.py`
  does the same locally (point `DATABASE_URL` at your Render DB's *external* URL
  to pull data to your laptop).
* **Not tied to Render.** The `Dockerfile` runs anywhere that hosts containers
  (Railway, Fly.io, a VPS…); set `ANTHROPIC_API_KEY` and `DATABASE_URL`, and the
  host must inject `$PORT` (Render does).
