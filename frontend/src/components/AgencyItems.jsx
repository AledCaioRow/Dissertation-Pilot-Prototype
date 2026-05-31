// Study-specific agency & clarity items (item 4 is the reverse-coded consistency check).
// Controlled: `value` keyed by 1-based item number -> score 1..5.
import React from "react";
import copy from "../content/copy.json";
import { Likert } from "./ui.jsx";

export default function AgencyItems({ value, onChange }) {
  const q = copy.questionnaire;
  return (
    <div>
      <h2>{q.agency_intro}</h2>
      <Likert items={q.agency_items} scale={q.scale} value={value} onChange={onChange} />
    </div>
  );
}
