// Phase 4/6 — Output: result rows + plain-language explanation + the exact SQL, together.
// The SQL is shown verbatim even though the participant may not read it (the overreliance
// probe). On an execution error, show a neutral message but still proceed to the ratings.
import React from "react";
import copy from "../content/copy.json";

export default function ResultView({ result, onNext }) {
  const o = copy.output;

  if (!result) {
    return (
      <div className="screen">
        <h1>{o.heading}</h1>
        <div className="c3-placeholder">
          <div className="ph-tag">output</div>
          <div className="ph-title">PLACEHOLDER — result not yet loaded</div>
          <div className="help">
            The query result appears here after the interface is submitted and the answer API
            call completes. (If you skipped the loading/interface screens, no result was fetched.)
          </div>
        </div>
        <div className="actions">
          <span className="spacer" />
          <button className="primary" onClick={onNext}>{o.button}</button>
        </div>
      </div>
    );
  }

  return (
    <div className="screen">
      <h1>{o.heading}</h1>

      {result.success ? (
        <>
          <p>{o.body}</p>
          <div className="result">
            {result.rows.length === 0 ? (
              <p className="muted">{o.empty}</p>
            ) : (
              <table>
                <thead>
                  <tr>{result.column_names.map((c) => <th key={c}>{c}</th>)}</tr>
                </thead>
                <tbody>
                  {result.rows.map((r, i) => (
                    <tr key={i}>{r.map((cell, j) => <td key={j}>{cell === null ? "" : String(cell)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <h2>{o.explanation_heading}</h2>
          <p>{result.explanation}</p>

          <h2>{o.sql_heading}</h2>
          <pre className="sql">{result.sql}</pre>
        </>
      ) : (
        <div className="error-box">{o.error}</div>
      )}

      <div className="actions">
        <span className="spacer" />
        <button className="primary" onClick={onNext}>{o.button}</button>
      </div>
    </div>
  );
}
