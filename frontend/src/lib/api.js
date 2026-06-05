// Backend base URL. Empty by default so requests use relative /api/* URLs that
// the Vite dev server proxies to the backend (see vite.config.js). Set
// VITE_API_BASE to point at a backend on another origin (e.g. a deployed API).
export const API_BASE = import.meta.env.VITE_API_BASE || "";

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
