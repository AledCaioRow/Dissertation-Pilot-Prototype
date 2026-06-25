// Backend base URL.
//  - Unset (local dev)        -> talk to the dev backend on :8000.
//  - Set to "" (the default in .env.production) -> same-origin, i.e. the
//    deployed combined service where FastAPI serves this app and /api together.
//  - Set to a full URL        -> a separate backend host (split deployment).
// `??` (not `||`) is deliberate so an explicit empty string keeps meaning
// "same-origin" instead of falling back to localhost.
export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = "";
    try { detail = (await res.json()).detail; } catch { /* ignore */ }
    throw new Error(`${path} failed (${res.status})${detail ? ": " + detail : ""}`);
  }
  return res.json();
}
