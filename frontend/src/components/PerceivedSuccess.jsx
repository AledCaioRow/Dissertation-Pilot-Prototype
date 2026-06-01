// The two-stage confidence screens. `stage` = "interface" (pre-result) or "answer" (post-result).
// Both are logged under the trial's perceived_success.
import React from "react";
import copy from "../content/copy.json";
import { RadioQuestion } from "./ui.jsx";

export default function PerceivedSuccess({ stage, value, onChange, onSubmit }) {
  const v = value || {};
  if (stage === "interface") {
    const c = copy.interface_confidence;
    return (
      <div className="screen">
        <RadioQuestion name="iface_conf" question={c.question} options={c.options}
          value={v.interface_confidence} onChange={(x) => onChange({ ...v, interface_confidence: x })} />
        <div className="actions">
          <span className="spacer" />
          <button className="primary" disabled={!v.interface_confidence} onClick={onSubmit}>
            {copy.nav.next}
          </button>
        </div>
      </div>
    );
  }

  const a = copy.answer_confidence;
  const ready = v.answer_wanted && v.answer_confidence;
  return (
    <div className="screen">
      <RadioQuestion name="ans_wanted" question={a.wanted_question} options={a.wanted_options}
        value={v.answer_wanted} onChange={(x) => onChange({ ...v, answer_wanted: x })} />
      <RadioQuestion name="ans_conf" question={a.confidence_question} options={a.confidence_options}
        value={v.answer_confidence} onChange={(x) => onChange({ ...v, answer_confidence: x })} />
      <div className="actions">
        <span className="spacer" />
        <button className="primary" disabled={!ready} onClick={onSubmit}>{a.button}</button>
      </div>
    </div>
  );
}
