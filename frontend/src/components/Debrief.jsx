// Phase 8 — Debrief (no Back once submitted): overall preference + open-ended.
import React from "react";
import copy from "../content/copy.json";
import { RadioQuestion } from "./ui.jsx";

export default function Debrief({ value, onChange, onSubmit }) {
  const d = copy.debrief;
  const v = value || {};
  const set = (k, x) => onChange({ ...v, [k]: x });

  return (
    <div className="screen">
      <h1>{d.heading}</h1>
      <RadioQuestion name="preference" question={d.preference_question} options={d.preference_options}
        value={v.preference} onChange={(x) => set("preference", x)} />
      {d.open_items.map((q, i) => (
        <div key={i}>
          <label>{q}</label>
          <textarea value={v[`open_${i}`] || ""} onChange={(e) => set(`open_${i}`, e.target.value)} />
        </div>
      ))}
      <div className="actions">
        <span className="spacer" />
        <button className="primary" disabled={!v.preference} onClick={onSubmit}>{d.button}</button>
      </div>
    </div>
  );
}
