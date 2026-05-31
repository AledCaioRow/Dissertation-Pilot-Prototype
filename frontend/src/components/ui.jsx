// Small shared UI pieces used across several screens.
import React from "react";
import copy from "../content/copy.json";

// A controlled Likert block. `value` is an object keyed by 1-based item number -> score (1..N).
export function Likert({ items, scale, value, onChange }) {
  const set = (idx, score) => onChange({ ...value, [idx + 1]: score });
  return (
    <div>
      {items.map((stmt, idx) => (
        <div className="likert" key={idx}>
          <div className="stmt">{idx + 1}. {stmt}</div>
          <div className="scale">
            {scale.map((lab, s) => (
              <label key={s}>
                <input type="radio" name={`likert_${idx}`} checked={value[idx + 1] === s + 1}
                  onChange={() => set(idx, s + 1)} />
                {lab}
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// A single multiple-choice question (confidence screens, preference, etc.).
export function RadioQuestion({ name, question, options, value, onChange }) {
  return (
    <div style={{ margin: "10px 0 18px" }}>
      <div className="stmt" style={{ marginBottom: 6 }}>{question}</div>
      {options.map((opt) => (
        <label className="choice" key={opt}>
          <input type="radio" name={name} checked={value === opt} onChange={() => onChange(opt)} />
          <span>{opt}</span>
        </label>
      ))}
    </div>
  );
}

// The persistent footer (from the study-explanation screen onward).
export function Footer({ onWithdraw }) {
  const exit = () => {
    if (window.confirm(copy.footer.exit_confirm)) onWithdraw();
  };
  return (
    <div className="footer">
      <span>{copy.footer.contact}</span>
      <span>·</span>
      <button className="link" onClick={exit}>{copy.footer.exit}</button>
    </div>
  );
}
