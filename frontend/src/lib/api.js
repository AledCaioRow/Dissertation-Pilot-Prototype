// Backend base URL. Override with VITE_API_BASE in an .env file if needed.
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

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
