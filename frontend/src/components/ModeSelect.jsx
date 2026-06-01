// Page 0 (researcher set-up): choose how the system answers for this session — stubbed
// canned responses, or a live Anthropic call (key in backend/.env). Stored per session via
// POST /session/mode; the backend threads it through every model call. Not a participant
// screen, so it may mention the API/stub plainly.
import React from "react";
import copy from "../content/copy.json";

export default function ModeSelect({ defaultUseStub = true, onSubmit }) {
  const m = copy.mode;
  const [choice, setChoice] = React.useState(defaultUseStub ? "stub" : "live");

  return (
    <div className="screen">
      <h1>{m.heading}</h1>
      <p className="muted">{m.body}</p>

      <div className="card">
        <label className="choice">
          <input type="radio" name="mode" checked={choice === "stub"} onChange={() => setChoice("stub")} />
          <span><strong>{m.stub_label}</strong><span className="snippet"> — {m.stub_help}</span></span>
        </label>
        <label className="choice">
          <input type="radio" name="mode" checked={choice === "live"} onChange={() => setChoice("live")} />
          <span><strong>{m.live_label}</strong><span className="snippet"> — {m.live_help}</span></span>
        </label>
      </div>

      {choice === "live" && <div className="nudge">{m.live_warning}</div>}

      <div className="actions">
        <span className="spacer" />
        <button className="primary" onClick={() => onSubmit(choice === "stub")}>{m.button}</button>
      </div>
    </div>
  );
}
