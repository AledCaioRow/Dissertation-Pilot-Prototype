// Phase 3b — one authoring screen (Back enabled). The participant never sees the class.
import React from "react";
import copy from "../content/copy.json";
import SchemaCard from "./SchemaCard.jsx";

export default function QuestionAuthor({ slot, schema, value, onChange, onSubmit, onBack, canBack, minChars }) {
  const a = copy.authoring;
  const prompt = a[`${slot.database}:${slot.ambiguity_class}`] || { task: "", then: "" };
  const v = value || { question: "", intent: "" };
  const set = (k, x) => onChange({ ...v, [k]: x });
  const text = (v.question || "").trim();
  const short = text.length > 0 && text.length < (minChars || 0);

  return (
    <div className="screen">
      <h1>Your question</h1>
      <p>{prompt.task}</p>
      <p className="muted">{a.intro}</p>
      <SchemaCard schema={schema} />

      <label>{a.question_label}</label>
      <textarea value={v.question || ""} onChange={(e) => set("question", e.target.value)} />
      {short && <div className="nudge">{a.nudge}</div>}

      <label>{a.intent_label}</label>
      <div className="help">{prompt.then}</div>
      <textarea value={v.intent || ""} onChange={(e) => set("intent", e.target.value)} />

      <div className="actions">
        {canBack ? <button onClick={onBack}>{copy.nav.back}</button> : <span />}
        <span className="spacer" />
        <button className="primary" disabled={!text} onClick={onSubmit}>{a.button}</button>
      </div>
    </div>
  );
}
