// Session API client. The study runs locally: the backend (FastAPI) and this frontend both
// run on the researcher's laptop, so every call hits the backend via the /api proxy.
const BASE = "/api";

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} failed (${res.status}): ${await res.text()}`);
  return res.json();
}

async function get(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`${path} failed (${res.status}): ${await res.text()}`);
  return res.json();
}

export const api = {
  getConfig: () => get("/config"),
  startSession: (participant_id) => post("/session/start", { participant_id }),
  setMode: (participant_id, use_stub) => post("/session/mode", { participant_id, use_stub }),
  consent: (payload) => post("/session/consent", payload),
  screening: (payload) => post("/session/screening", payload),
  getSchema: (name) => get(`/schema/${name}`),
  author: (payload) => post("/author", payload),
  trialInterface: (participant_id, trial_id) => post("/trial/interface", { participant_id, trial_id }),
  trialAnswer: (payload) => post("/trial/answer", payload),
  perceived: (payload) => post("/trial/perceived", payload),
  questionnaire: (payload) => post("/questionnaire", payload),
  debrief: (payload) => post("/debrief", payload),
  withdraw: (participant_id) => post("/session/withdraw", { participant_id }),
};
