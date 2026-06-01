// Session API client.
//
// The wizard can run two ways:
//   * with the backend ("real" mode) — every call hits FastAPI via the /api proxy;
//   * standalone ("mock" mode) — if the backend isn't reachable, calls are served by
//     mockApi.js so you can run `npm run dev` and click through the wizard with no Python.
//
// `detectMode()` is called once at startup; after that `api.*` routes to whichever is live.
import { mockApi } from "./mockApi.js";

const BASE = "/api";

async function rawPost(path, body) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} failed (${res.status}): ${await res.text()}`);
  return res.json();
}

async function rawGet(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`${path} failed (${res.status}): ${await res.text()}`);
  return res.json();
}

const realApi = {
  getConfig: () => rawGet("/config"),
  startSession: (participant_id) => rawPost("/session/start", { participant_id }),
  consent: (payload) => rawPost("/session/consent", payload),
  screening: (payload) => rawPost("/session/screening", payload),
  getSchema: (name) => rawGet(`/schema/${name}`),
  author: (payload) => rawPost("/author", payload),
  trialInterface: (participant_id, trial_id) => rawPost("/trial/interface", { participant_id, trial_id }),
  trialAnswer: (payload) => rawPost("/trial/answer", payload),
  perceived: (payload) => rawPost("/trial/perceived", payload),
  questionnaire: (payload) => rawPost("/questionnaire", payload),
  debrief: (payload) => rawPost("/debrief", payload),
  withdraw: (participant_id) => rawPost("/session/withdraw", { participant_id }),
};

let MODE = null; // "real" | "mock"

export async function detectMode() {
  try {
    await rawGet("/config");
    MODE = "real";
  } catch {
    MODE = "mock";
  }
  if (typeof window !== "undefined") window.__API_MODE = MODE;
  return MODE;
}

export function apiMode() {
  return MODE;
}

const pick = () => (MODE === "mock" ? mockApi : realApi);

// Routes every call to the live backend or the mock, decided by detectMode().
export const api = new Proxy({}, { get: (_t, prop) => (...args) => pick()[prop](...args) });
