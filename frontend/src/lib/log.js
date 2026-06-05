// Client-side logging: starts a session, buffers interaction events, and flushes
// them to /api/log on an interval, on screen_leave, and on tab close (sendBeacon).
// Nothing about the UI changes — this is attached additively to existing controls.

import { API_BASE, postJSON } from "./api.js";

let sessionId = null;
let conditionOrder = ["1", "2", "3"];
let buffer = [];
let flushTimer = null;

const FLUSH_MS = 3000;

export function getSessionId() { return sessionId; }
export function getConditionOrder() { return conditionOrder; }

export async function startSession(meta = {}) {
  const body = {
    demographics: meta.demographics || null,
    condition_order: meta.condition_order || null,
    user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
  };
  const out = await postJSON("/api/session/start", body);
  sessionId = out.session_id;
  if (out.condition_order) conditionOrder = out.condition_order;
  startTimer();
  installUnloadFlush();
  return out;
}

// Buffer one event. `payload` may carry screen/condition/question_index/target_id/value.
export function logEvent(type, payload = {}) {
  if (!sessionId) return; // session not started yet; drop pre-session noise
  buffer.push({
    session_id: sessionId,
    event_type: type,
    screen: payload.screen ?? null,
    condition: payload.condition ?? null,
    question_index: payload.question_index ?? null,
    target_id: payload.target_id ?? null,
    value_json: payload.value ?? payload.value_json ?? null,
    elapsed_ms: payload.elapsed_ms ?? null,
    ts_client: new Date().toISOString(),
  });
  if (buffer.length >= 25) flush();
}

export async function flush() {
  if (!sessionId || buffer.length === 0) return;
  const events = buffer;
  buffer = [];
  try {
    await postJSON("/api/log", { events });
  } catch (e) {
    // Put them back so nothing is lost; they'll go out on the next flush.
    buffer = events.concat(buffer);
    // eslint-disable-next-line no-console
    console.warn("log flush failed, will retry", e);
  }
}

function startTimer() {
  if (flushTimer) return;
  flushTimer = setInterval(flush, FLUSH_MS);
}

function installUnloadFlush() {
  if (typeof window === "undefined") return;
  window.addEventListener("beforeunload", () => {
    if (!sessionId || buffer.length === 0) return;
    const payload = JSON.stringify({ events: buffer });
    buffer = [];
    if (navigator.sendBeacon) {
      navigator.sendBeacon(`${API_BASE}/api/log`, new Blob([payload], { type: "application/json" }));
    }
  });
}
