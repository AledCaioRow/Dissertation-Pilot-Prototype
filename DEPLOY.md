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

## Part 1 — Get set up (one-time, ~10 minutes)

You need three things. The first is already done; the other two are free
accounts you create once.

### 1. The code on GitHub ✅ (already done)
It's on the **`online-version`** branch of your repository — nothing to do here.

### 2. An Anthropic API key (this powers the model)
This is the key that lets the study talk to the Claude model.

1. Go to <https://console.anthropic.com> and sign up or log in.
2. Add a little credit: open **Billing** (or **Plans**) and add a payment method
   / buy credits. The model is **pay-as-you-go** and is *separate* from the free
   Render hosting — for a pilot it's usually only **a few pounds**. (Without any
   credit, the model steps in the study will error.)
3. Open **API Keys** → **Create Key**, give it any name, and **copy** the value.
   It looks like `sk-ant-...`. Treat it like a password — you'll paste it into
   Render in Part 2. If you lose it, just create another one.

### 3. A Render account (this hosts the website)
Render is the service that turns the code into a live website.

1. Go to <https://render.com> and click **Get Started** / **Sign up**.
2. Choose **Sign up with GitHub** and log in to GitHub if asked.
3. When GitHub asks, **authorise Render** to access your repositories — you can
   limit it to just `Dissertation-Pilot-Prototype`. This is what lets Render see
   your code in Part 2.

That's the setup. Everything from here is clicking buttons.

---

## What this costs: £0 for now

`render.yaml` is set to Render's **free** plans, so the **hosting** costs
**nothing**. (The Claude model itself is pay-as-you-go on your Anthropic account
— see Part 1 — usually just a few pounds for a pilot.) That's ideal for building
it and testing. Two things to know about the free hosting:

| Piece | On Free | What that means |
| --- | --- | --- |
| **Website** | sleeps when idle | After ~15 min with no visitors it sleeps; the next visit takes ~30–60s to wake, then it's normal. |
| **Database** | **deleted after ~30 days** | Render removes a free database about 30 days after you create it. **Before then**, either upgrade it (keeps your data) or export your data — otherwise it's lost. |

For **real participant sessions** later, upgrade to the small paid plans
(~$13/month total) so the site stays awake and your data is kept safely — see
**[Upgrade to the paid version](#upgrade-to-the-paid-version)** below. It's a
2-minute change and you only pay while you're collecting data.

---

## Part 2 — Make the website (deploy)

This one process creates the live website **and** its database together. It
takes ~10 minutes, mostly waiting.

1. Go to <https://dashboard.render.com> (you'll already be logged in from
   Part 1).
2. Click **New +** (top-right) → **Blueprint**.
3. Find and select your repository, **`Dissertation-Pilot-Prototype`**. If it's
   not listed, click **Configure account** / **Configure in GitHub**, give
   Render access to it, then come back.
4. For **Branch**, choose **`online-version`** (not `main`). This matters — the
   website's configuration lives on that branch.
5. Render reads the project's `render.yaml` and shows the **two resources** it's
   about to create:
   * `student-club-study` — the website, and
   * `student-club-study-db` — the database.

   Click **Apply** (sometimes labelled **Create** or **Deploy Blueprint**).
6. Render asks you to fill in the one secret it needs:
   * **ANTHROPIC_API_KEY** → paste the `sk-ant-...` key from Part 1.

   You don't need to set anything else — `ADMIN_TOKEN` is generated for you and
   the database is connected automatically.
7. Confirm, and **wait**. The first build takes about **5–10 minutes** while
   Render builds the app and creates the database. You can watch the log scroll;
   it's ready when the website's status turns **"Live"** (green).

**You now have a website.** Render shows its address near the top of the
`student-club-study` page — something like
`https://student-club-study.onrender.com`. That link *is* your study; the next
section confirms it works.

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
