# Putting the study online (plain-English guide)

This guide turns the study into a **website with one link** you can send to
participants, so nobody has to install anything or run commands. No technical
knowledge is needed — just follow the steps.

You'll deploy to **Render**, which builds the app straight from GitHub. The
project already contains everything Render needs (a `Dockerfile` and a
`render.yaml`), so you mostly just click buttons.

---

## What you'll end up with

* A single web address like `https://student-club-study.onrender.com`.
* Opening it shows the study exactly as it looks locally.
* Everything participants do is saved on the server.
* You can download all collected data from your browser whenever you like.

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

## One decision first: free vs. paid (about £6/$7 a month)

Your study **saves participant data to a file on the server.** Render has two
relevant options:

| Option | Monthly cost | What happens to your data |
| --- | --- | --- |
| **Starter plan + disk** (recommended) | ~$7 | Data is kept safely, even when the app restarts or you update it. |
| **Free plan** | $0 | Good for *testing*. The server wipes its files whenever it restarts or sleeps, so **collected data can be lost**. The free server also "sleeps" after 15 minutes idle and takes ~30–60s to wake. |

**For real participants, use Starter** so you don't lose data. For a quick try,
Free is fine. The steps below assume Starter (the default in `render.yaml`); a
note at the end explains how to switch to Free.

---

## Step-by-step: deploy on Render

1. Go to <https://dashboard.render.com> and log in.
2. Click **New +** (top right) → **Blueprint**.
3. Choose your repository (`Dissertation-Pilot-Prototype`). If you don't see it,
   click *Configure account* and give Render access to the repo.
4. When asked for the **branch**, choose **`online-version`**.
5. Render reads `render.yaml` and shows a service called **student-club-study**.
   Click **Apply** / **Create**.
6. Render will ask you to fill in the secret value it needs:
   * **ANTHROPIC_API_KEY** → paste your `sk-ant-...` key.
   (You don't need to touch the others — `ADMIN_TOKEN` is generated for you.)
7. Click **Apply** / **Deploy** and wait. The first build takes about
   **5–10 minutes** (it's installing and building everything). You can watch the
   log scroll by; you're done when it says **"Live"**.

That's it — Render shows your web address near the top of the service page.

---

## Check it works

1. Click your new web address (e.g. `https://student-club-study.onrender.com`).
   You should see the study's first screen.
2. Add `/api/health` to the end of the address
   (e.g. `https://student-club-study.onrender.com/api/health`). You should see
   `{"ok":true,...}`. That confirms the server is healthy.
3. Do one full run-through yourself as a test participant.

> If a model step shows an error, the most likely cause is the API key. Go to
> the service's **Environment** tab, check `ANTHROPIC_API_KEY` is correct, and
> that your Anthropic account has credit.

---

## Give it to participants

Just send them the web address. Nothing to install. Each person who opens it
gets their own session, and their answers are saved automatically.

---

## Get your data back out

Your data lives in a single file on the server. To download it:

1. Find your secret download token: in Render, open the service →
   **Environment** tab → copy the value of **`ADMIN_TOKEN`**.
2. In your browser, go to:

   ```
   https://YOUR-APP.onrender.com/api/admin/export?token=PASTE_THE_TOKEN_HERE
   ```

   This downloads a file called **`study_logs.sqlite`** containing everything.

**To read it**, either:

* Open it with the free app **DB Browser for SQLite**
  (<https://sqlitebrowser.org>) — point-and-click, no coding; **or**
* Turn it into spreadsheets (CSV): put the downloaded `study_logs.sqlite` into
  the project's `backend/logs/` folder, then run:

  ```bash
  cd backend
  python scripts/export_csv.py        # writes one .csv per table into logs/csv/
  ```

> Keep your `ADMIN_TOKEN` private — anyone who has it can download the data.
> If it ever leaks, change it in Render's Environment tab (the app redeploys and
> the old token stops working). If you remove the token entirely, the download
> link is switched off (returns "Not found").

---

## Updating the study later

Any time you push a change to the `online-version` branch on GitHub, Render
rebuilds and redeploys automatically. Your saved data is kept (on the Starter
plan). You don't have to repeat the setup.

---

## If you'd rather trial it for free (data not kept)

Edit `render.yaml` before deploying (or in Render's settings):

* change `plan: starter` to `plan: free`, and
* delete the whole `disk:` block at the bottom.

Everything else is the same. Just remember: on Free, **export your data often**,
because a restart can wipe it.

---

## Troubleshooting

| Symptom | Likely fix |
| --- | --- |
| Build fails immediately | Make sure you selected the **`online-version`** branch in the Blueprint step. |
| Page loads but model steps error | Check `ANTHROPIC_API_KEY` in the Environment tab and that your Anthropic account has credit. |
| First visit is very slow | On the **Free** plan the server sleeps when idle and takes ~30–60s to wake. Starter stays awake. |
| `/api/admin/export` says "Not found" | `ADMIN_TOKEN` isn't set. Add one in the Environment tab (Starter generates one automatically). |
| Data disappeared after an update | You're on **Free** with no disk. Switch to **Starter** + disk for real data collection. |

---

## For the technically curious (optional)

* **One service, one origin.** A multi-stage `Dockerfile` builds the React app
  (`frontend/`) and copies it next to the FastAPI backend, which serves the UI
  and the `/api/*` routes together. No CORS, one URL.
* **Same-origin frontend.** `frontend/.env.production` sets `VITE_API_BASE=""`,
  so the built app calls `/api` on its own host.
* **Data persistence.** Logs are written to `STUDY_LOG_DIR` (`/data/logs`),
  which is the Render disk mounted at `/data`.
* **Not tied to Render.** The `Dockerfile` runs anywhere that hosts containers
  (Railway, Fly.io, a VPS…). Render is just the easiest starting point. The host
  must inject `$PORT` (Render does) and, for durable data, mount a volume and
  point `STUDY_LOG_DIR` at it.
