// Phase 2 — Study explanation (Back enabled).
import React from "react";
import copy from "../content/copy.json";

export default function StudyExplanation({ onNext, onBack, canBack }) {
  const s = copy.study_explanation;
  return (
    <div className="screen">
      <h1>{s.heading}</h1>
      <p>{s.body}</p>
      <div className="actions">
        {canBack ? <button onClick={onBack}>{copy.nav.back}</button> : <span />}
        <span className="spacer" />
        <button className="primary" onClick={onNext}>{s.button}</button>
      </div>
    </div>
  );
}
