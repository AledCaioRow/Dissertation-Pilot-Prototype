// System Usability Scale (canonical Brooke 1996 wording — see copy.json, do not paraphrase).
// Controlled: `value` keyed by 1-based item number -> score 1..5.
import React from "react";
import copy from "../content/copy.json";
import { Likert } from "./ui.jsx";

export default function SUS({ value, onChange }) {
  const q = copy.questionnaire;
  return (
    <div>
      <h2>{q.sus_intro}</h2>
      <Likert items={q.sus_items} scale={q.scale} value={value} onChange={onChange} />
    </div>
  );
}
