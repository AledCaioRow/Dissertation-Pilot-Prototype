import { useEffect, useState } from "react";

// Shared result stage for output-1/2/3. Held CONSTANT across conditions — only
// the interface before it varies, so this screen is identical for all three.
// Fed by /api/finalize via the `result` prop:
//   { explanation, confidence, sql, queries: [{ sql, columns, preview_rows, total_count }],
//     columns, preview_rows, total_count }
// `queries` may hold more than one result table (the model can emit several
// SELECTs); the single-result fields mirror the first query for older callers.

const TEAL = "#156082";
const LIGHT = "#E8E8E8";
const BLACK = "#000000";
const WHITE = "#FFFFFF";
const FONT = "Arial, Helvetica, sans-serif";
const MONO = "'Courier New', ui-monospace, monospace";
const BORDER = `3px solid ${BLACK}`;

export default function OutputStage({ result, loading, error, onLog }) {
  const [sqlOpen, setSqlOpen] = useState(false);

  useEffect(() => {
    if (result) onLog?.("output_view", { value: { total_count: result.total_count } });
  }, [result]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div style={wrap}>
        <div style={{ fontSize: 20, fontWeight: 700 }}>Building your answer…</div>
        <div style={{ fontSize: 16, color: "#333", marginTop: 8 }}>
          The system is turning your clarified question into a query and running it.
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={wrap}>
        <div style={{ fontSize: 20, fontWeight: 700, color: "#7a1f1f" }}>
          Something went wrong producing the answer.
        </div>
        <div style={{ fontFamily: MONO, fontSize: 14, marginTop: 10, background: LIGHT, padding: 12, border: BORDER }}>
          {String(error)}
        </div>
      </div>
    );
  }

  if (!result) return <div style={wrap} />;

  const { explanation, confidence, sql } = result;
  // Normalise to a list of result tables. Prefer `queries`; fall back to the
  // single-result fields so older finalize payloads still render.
  const queries = (result.queries && result.queries.length)
    ? result.queries
    : [{ sql, columns: result.columns || [], preview_rows: result.preview_rows || [], total_count: result.total_count || 0 }];
  const multi = queries.length > 1;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14, color: BLACK }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>The answer</h1>

      {/* explanation */}
      <div style={{ background: WHITE, border: BORDER, padding: 16 }}>
        <div style={label}>What this returns</div>
        <div style={{ fontSize: 17, lineHeight: 1.45 }}>{explanation}</div>
      </div>

      {/* confidence */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={label}>Confidence</span>
        <div style={{ flex: 1, height: 18, background: LIGHT, border: `2px solid ${BLACK}` }}>
          <div style={{ width: `${confidence ?? 0}%`, height: "100%", background: TEAL }} />
        </div>
        <span style={{ fontFamily: MONO, fontSize: 15 }}>{confidence ?? "—"}/100</span>
      </div>

      {/* collapsible SQL */}
      <div>
        <button
          onClick={() => { setSqlOpen((o) => !o); onLog?.("output_sql_expand", { value: { open: !sqlOpen } }); }}
          style={{ fontFamily: FONT, fontSize: 15, border: BORDER, background: WHITE, padding: "6px 12px", cursor: "pointer", borderRadius: 0 }}
        >
          {sqlOpen ? "▾ Hide the query that ran" : "▸ Show the query that ran"}
        </button>
        {sqlOpen && (
          <pre style={{ margin: "8px 0 0", background: "#0f2933", color: "#dbeaf0", padding: 14, fontFamily: MONO, fontSize: 14, overflowX: "auto", border: BORDER }}>
            {sql}
          </pre>
        )}
      </div>

      {/* result rows (scrollable, up to 15 per query) */}
      <div style={{ flex: "1 1 auto", minHeight: 0, display: "flex", flexDirection: "column", gap: 14, overflowY: multi ? "auto" : "visible" }}>
        <div style={label}>{multi ? `Results (${queries.length} tables)` : "Results"}</div>
        {queries.map((qr, qi) => (
          <ResultTable key={qi} index={qi} total={queries.length} query={qr} />
        ))}
      </div>
    </div>
  );
}

// One result table for a single SELECT. Several may be shown when the model
// emitted more than one query.
function ResultTable({ index, total, query }) {
  const { columns = [], preview_rows = [], total_count = 0 } = query;
  const multi = total > 1;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: multi ? "0 0 auto" : "1 1 auto", minHeight: multi ? "auto" : 80 }}>
      {multi && <div style={{ ...label, marginBottom: 4 }}>Table {index + 1} of {total}</div>}
      <div style={{ flex: multi ? "0 0 auto" : "1 1 auto", minHeight: 80, maxHeight: multi ? 240 : "none", overflow: "auto", border: BORDER, background: WHITE }}>
        {columns.length === 0 ? (
          <div style={{ padding: 16, fontSize: 15 }}>No columns returned.</div>
        ) : (
          <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
            <thead>
              <tr>
                {columns.map((c) => (
                  <th key={c} style={th}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview_rows.map((row, i) => (
                <tr key={i} style={{ background: i % 2 ? "#f4f4f4" : WHITE }}>
                  {columns.map((c) => (
                    <td key={c} style={td}>{formatCell(row[c])}</td>
                  ))}
                </tr>
              ))}
              {preview_rows.length === 0 && (
                <tr><td style={td} colSpan={columns.length}>No rows matched.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
      <div style={{ fontSize: 14, marginTop: 6, fontWeight: 700 }}>
        Total returned: {total_count}
        {total_count > preview_rows.length && (
          <span style={{ fontWeight: 400, color: "#444" }}> (showing first {preview_rows.length})</span>
        )}
      </div>
    </div>
  );
}

function formatCell(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return String(v);
  return String(v);
}

const wrap = { fontFamily: FONT, color: BLACK, padding: 8 };
const label = { fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: "#5f6b70", marginBottom: 6 };
const th = { textAlign: "left", padding: "8px 10px", borderBottom: `2px solid ${BLACK}`, position: "sticky", top: 0, background: TEAL, color: WHITE, fontFamily: FONT };
const td = { padding: "6px 10px", borderBottom: "1px solid #ccc", fontFamily: MONO, whiteSpace: "nowrap" };
