/**
 * The C3 component primitive set — the ONLY controls model-generated JSX may use.
 * Mirrors docs/spec/dynamic_interface.md §3 (the single source of truth). If you add or
 * remove a primitive, change it here, in the host's injected scope (PRIMITIVE_NAMES), and
 * in the C3 prompt's `{primitives}` block (backend/calls/__init__.py:primitives_block).
 *
 * Every control is presentational + controlled: it takes `value` and `onChange`, plus
 * `id`, `label`, `help`, and (where relevant) `options` / `min` / `max` / `step`. The
 * generated component owns the state and calls submitResponses({...}) once on submit.
 */
import React from "react";

// ColumnPicker reads the current schema's qualified columns from here when it isn't
// given an explicit `options` list. The host provides the value.
export const SchemaColumnsContext = React.createContext([]);

function Field({ label, help, children }) {
  return (
    <div style={{ margin: "12px 0" }}>
      {label && <label>{label}</label>}
      {help && <div className="help">{help}</div>}
      {children}
    </div>
  );
}

export function Radio({ id, label, help, options = [], value, onChange }) {
  return (
    <Field label={label} help={help}>
      {options.map((o) => (
        <label className="choice" key={o.value}>
          <input type="radio" name={id} checked={value === o.value}
            onChange={() => onChange(o.value)} />
          <span>{o.label}{o.help && <span className="snippet"> — {o.help}</span>}</span>
        </label>
      ))}
    </Field>
  );
}

export function Checkboxes({ id, label, help, options = [], value = [], onChange }) {
  const toggle = (v) =>
    onChange(value.includes(v) ? value.filter((x) => x !== v) : [...value, v]);
  return (
    <Field label={label} help={help}>
      {options.map((o) => (
        <label className="choice" key={o.value}>
          <input type="checkbox" checked={value.includes(o.value)} onChange={() => toggle(o.value)} />
          <span>{o.label}{o.help && <span className="snippet"> — {o.help}</span>}</span>
        </label>
      ))}
    </Field>
  );
}

export function Dropdown({ id, label, help, options = [], value, onChange }) {
  return (
    <Field label={label} help={help}>
      <select value={value ?? ""} onChange={(e) => onChange(e.target.value)}>
        <option value="" disabled>Choose…</option>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </Field>
  );
}

export function MultiSelect({ id, label, help, options = [], value = [], onChange }) {
  // Rendered as a checkbox list — clearer for non-experts than a ctrl-click multi-select.
  return <Checkboxes id={id} label={label} help={help} options={options} value={value} onChange={onChange} />;
}

export function NumberInput({ id, label, help, value, onChange, min, max, step }) {
  return (
    <Field label={label} help={help}>
      <input type="number" value={value ?? ""} min={min} max={max} step={step}
        onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))} />
    </Field>
  );
}

export function Slider({ id, label, help, value, onChange, min = 0, max = 100, step = 1 }) {
  return (
    <Field label={label} help={help}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <input type="range" style={{ flex: 1 }} min={min} max={max} step={step}
          value={value ?? min} onChange={(e) => onChange(Number(e.target.value))} />
        <strong style={{ minWidth: 40, textAlign: "right" }}>{value ?? min}</strong>
      </div>
    </Field>
  );
}

export function DatePicker({ id, label, help, value, onChange }) {
  return (
    <Field label={label} help={help}>
      <input type="date" value={value ?? ""} onChange={(e) => onChange(e.target.value)} />
    </Field>
  );
}

export function DateRange({ id, label, help, value = {}, onChange }) {
  const set = (k, v) => onChange({ ...value, [k]: v });
  return (
    <Field label={label} help={help}>
      <div className="row">
        <div>
          <div className="help">From</div>
          <input type="date" value={value.start ?? ""} onChange={(e) => set("start", e.target.value)} />
        </div>
        <div>
          <div className="help">To</div>
          <input type="date" value={value.end ?? ""} onChange={(e) => set("end", e.target.value)} />
        </div>
      </div>
    </Field>
  );
}

export function Toggle({ id, label, help, value = false, onChange }) {
  return (
    <Field help={help}>
      <label className="choice">
        <input type="checkbox" checked={!!value} onChange={(e) => onChange(e.target.checked)} />
        <span>{label}</span>
      </label>
    </Field>
  );
}

export function ColumnPicker({ id, label, help, options, value, onChange }) {
  const ctxColumns = React.useContext(SchemaColumnsContext);
  const cols = (options && options.length ? options : ctxColumns).map((c) =>
    typeof c === "string" ? { value: c, label: c } : c
  );
  return <Dropdown id={id} label={label} help={help} options={cols} value={value} onChange={onChange} />;
}

export function TextInput({ id, label, help, value, onChange }) {
  return (
    <Field label={label} help={help}>
      <input type="text" value={value ?? ""} onChange={(e) => onChange(e.target.value)} />
    </Field>
  );
}

export function InfoPanel({ label, help }) {
  return (
    <div className="card">
      {label && <strong>{label}</strong>}
      {help && <div className="help" style={{ marginTop: 4 }}>{help}</div>}
    </div>
  );
}

// The injected scope, in a fixed order shared with the host's `new Function` mount.
export const PRIMITIVES = {
  Radio, Checkboxes, Dropdown, MultiSelect, NumberInput, Slider,
  DatePicker, DateRange, Toggle, ColumnPicker, TextInput, InfoPanel,
};
export const PRIMITIVE_NAMES = Object.keys(PRIMITIVES);
