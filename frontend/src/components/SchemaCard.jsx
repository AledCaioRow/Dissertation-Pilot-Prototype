// Bland, read-only rendering of a schema for the authoring screens.
import React from "react";

export default function SchemaCard({ schema }) {
  if (!schema) return <p className="muted">Loading the records…</p>;
  return (
    <div className="schema card">
      {schema.placeholder && (
        <p className="muted">(Sample structure shown — the live records aren't loaded yet.)</p>
      )}
      {schema.tables.map((t) => (
        <div key={t.name}>
          <div className="tname">{t.name}</div>
          <table>
            <tbody>
              {t.columns.map((c) => (
                <tr key={c.name}>
                  <td>{c.name}</td>
                  <td className="muted">{c.type}{c.pk ? " · key" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
