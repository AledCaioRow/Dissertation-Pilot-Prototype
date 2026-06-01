// Phase 1 (details) — brief demographics: age band + SQL/DB experience (build brief §15).
import React from "react";
import copy from "../content/copy.json";

function Select({ field, value, onChange }) {
  return (
    <div>
      <label>{field.label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="" disabled>Choose…</option>
        {field.options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

export default function Screening({ value, onChange, onSubmit, onBack, canBack }) {
  const s = copy.screening;
  const v = value || {};
  const set = (k, val) => onChange({ ...v, [k]: val });
  const ready = v.age_band && v.sql_experience && v.db_experience;

  return (
    <div className="screen">
      <h1>{s.heading}</h1>
      <p>{s.body}</p>
      <Select field={s.age_band} value={v.age_band || ""} onChange={(x) => set("age_band", x)} />
      <Select field={s.sql_experience} value={v.sql_experience || ""} onChange={(x) => set("sql_experience", x)} />
      <Select field={s.db_experience} value={v.db_experience || ""} onChange={(x) => set("db_experience", x)} />
      <div className="actions">
        {canBack ? <button onClick={onBack}>{copy.nav.back}</button> : <span />}
        <span className="spacer" />
        <button className="primary" disabled={!ready} onClick={onSubmit}>{s.button}</button>
      </div>
    </div>
  );
}
