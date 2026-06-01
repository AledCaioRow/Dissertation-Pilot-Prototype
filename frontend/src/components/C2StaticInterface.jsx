/**
 * C2 — the faithful AmbiSQL static clarifier (docs/spec/ambisql_static_interface.md §5).
 *
 * Structure is CONSTANT across every question: a standing instruction (rendered by the
 * parent), then a stacked list of clarification cards — each a question + description +
 * radio group of options carrying a database snippet — then the optional additional-
 * constraints free-text box, then one Submit. Multiple-choice ONLY: never a slider, date
 * picker, toggle, or any adaptive control. That affordance limit is the experiment.
 */
import React from "react";
import copy from "../content/copy.json";

export default function C2StaticInterface({ data, onSubmit }) {
  const widgets = data.widgets || [];
  const [choices, setChoices] = React.useState({});
  const [extra, setExtra] = React.useState("");
  const done = React.useRef(false);

  const allChosen = widgets.every((w) => choices[w.id] !== undefined);

  const submit = () => {
    if (done.current) return;
    done.current = true;
    const responses = widgets.map((w) => ({
      field_id: w.id,
      label: w.title,
      value: choices[w.id],
    }));
    if (data.allow_additional_constraints && extra.trim()) {
      responses.push({
        field_id: "additional_constraints",
        label: copy.interface.additional_constraints_label,
        value: extra.trim(),
      });
    }
    onSubmit(responses);
  };

  // Stub mode: show a labelled PLACEHOLDER box instead of invented widgets.
  if (data.placeholder) {
    const submitPlaceholder = () => {
      if (done.current) return;
      done.current = true;
      onSubmit([]);
    };
    return (
      <div>
        <div className="c3-placeholder">
          <div className="ph-tag">C2 · static clarifier</div>
          <div className="ph-title">PLACEHOLDER — C2 clarification interface</div>
          <div className="help">
            The real C2 interface is generated here from the model's call-1 output — multiple-choice
            clarification widgets based on detected ambiguities. In stub mode no content is generated;
            this box marks the slot. Set USE_STUB=False and provide ANTHROPIC_API_KEY to see actual widgets.
          </div>
        </div>
        <div className="actions">
          <span className="spacer" />
          <button className="primary" onClick={submitPlaceholder}>
            {copy.interface.submit_label}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {widgets.length === 0 && <p className="muted">{copy.interface.skip_note}</p>}

      {widgets.map((w) => (
        <div className="card" key={w.id}>
          <strong>{w.title}</strong>
          {w.description && <div className="help">{w.description}</div>}
          <div style={{ marginTop: 8 }}>
            {w.options.map((o) => (
              <label className="choice" key={o.value}>
                <input type="radio" name={w.id} checked={choices[w.id] === o.value}
                  onChange={() => setChoices({ ...choices, [w.id]: o.value })} />
                <span>
                  {o.label}
                  {o.snippet && <span className="snippet"> — {o.snippet}</span>}
                </span>
              </label>
            ))}
          </div>
        </div>
      ))}

      {data.allow_additional_constraints && (
        <div>
          <label>{copy.interface.additional_constraints_label}</label>
          <textarea value={extra} onChange={(e) => setExtra(e.target.value)} />
        </div>
      )}

      <div className="actions">
        <span className="spacer" />
        <button className="primary" disabled={!allChosen} onClick={submit}>
          {copy.interface.submit_label}
        </button>
      </div>
    </div>
  );
}
