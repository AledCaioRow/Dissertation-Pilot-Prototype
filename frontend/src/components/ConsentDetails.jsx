// Phase 1 — Consent & details (no Back). All checkboxes required to continue.
import React from "react";
import copy from "../content/copy.json";

export default function ConsentDetails({ participantId, onSubmit }) {
  const c = copy.consent;
  const [checked, setChecked] = React.useState(c.checkboxes.map(() => false));
  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");

  const allChecked = checked.every(Boolean);
  const toggle = (i) => setChecked(checked.map((v, idx) => (idx === i ? !v : v)));

  const begin = () => {
    const consent = {};
    c.checkboxes.forEach((_, i) => (consent[`item_${i + 1}`] = checked[i]));
    onSubmit({ name, email, consent, agreed: allChecked });
  };

  return (
    <div className="screen">
      <h1>{c.heading}</h1>
      <p>{c.body}</p>

      <div className="card">
        {c.checkboxes.map((label, i) => (
          <label className="choice" key={i}>
            <input type="checkbox" checked={checked[i]} onChange={() => toggle(i)} />
            <span>{label}</span>
          </label>
        ))}
      </div>

      <div className="row">
        <div>
          <label>{c.name_label}</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label>{c.email_label}</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
      </div>
      <label>{c.pid_label}</label>
      <input type="text" value={participantId ?? ""} readOnly />

      <div className="actions">
        <span className="spacer" />
        <button className="primary" disabled={!allChecked} onClick={begin}>{c.button}</button>
      </div>
    </div>
  );
}
