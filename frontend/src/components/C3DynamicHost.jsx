/**
 * C3 host — live-mounts the model's generated JSX in a sandbox (docs/spec/dynamic_interface.md §4).
 *
 * Babel-standalone transpiles the JSX; a scoped `new Function` mounts it with an injected
 * scope of { React, the §3 primitives, submitResponses }. The generated snippet must define a
 * component named `Interface` and call submitResponses({...}) once on its own submit button.
 *
 * Fallback: if the JSX fails to compile OR throws on render, we catch it and render a generic
 * component listing each manifest field as a labelled TextInput, reporting compile_success=false
 * (carried on the onSubmit call). The trial always proceeds; a compile failure never aborts it.
 */
import React from "react";
import * as Babel from "@babel/standalone";
import { PRIMITIVES, PRIMITIVE_NAMES, SchemaColumnsContext } from "./c3primitives.jsx";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { failed: false };
  }
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(err) {
    if (this.props.onError) this.props.onError(err);
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}

function buildComponent(jsx, submitResponses) {
  const code = Babel.transform(jsx, { presets: ["react"] }).code;
  const factory = new Function(
    "React",
    ...PRIMITIVE_NAMES,
    "submitResponses",
    `${code}\n; return typeof Interface !== "undefined" ? Interface : null;`
  );
  const Comp = factory(React, ...PRIMITIVE_NAMES.map((n) => PRIMITIVES[n]), submitResponses);
  if (!Comp) throw new Error("Generated code did not define an `Interface` component.");
  return Comp;
}

function C3Fallback({ fields, onSubmit }) {
  const [vals, setVals] = React.useState({});
  const done = React.useRef(false);
  const submit = () => {
    if (done.current) return;
    done.current = true;
    const responses = fields.map((f) => ({ field_id: f.id, label: f.label, value: vals[f.id] ?? "" }));
    onSubmit(responses, false); // compile_success = false
  };
  return (
    <div>
      <div className="card">
        <strong>Showing a simpler version</strong>
        <div className="help">Please type an answer for each.</div>
      </div>
      {fields.length === 0 && <p className="muted">There was nothing to ask about — you can carry on.</p>}
      {fields.map((f) => (
        <div key={f.id}>
          <label>{f.label}</label>
          <input type="text" value={vals[f.id] ?? ""}
            onChange={(e) => setVals({ ...vals, [f.id]: e.target.value })} />
        </div>
      ))}
      <div className="actions">
        <span className="spacer" />
        <button className="primary" onClick={submit}>Show me the answer</button>
      </div>
    </div>
  );
}

// The blank placeholder slot: shows WHERE the generated JSX will mount, without mounting
// anything. Only used for a genuinely empty payload (data.placeholder === true); in normal
// runs the stub/live call returns real JSX. The submit button lets the wizard proceed; it
// submits the manifest fields with empty values.
function C3Placeholder({ fields, onSubmit }) {
  const done = React.useRef(false);
  const proceed = () => {
    if (done.current) return;
    done.current = true;
    const responses = fields.map((f) => ({ field_id: f.id, label: f.label, value: "" }));
    onSubmit(responses, null);
  };
  return (
    <div>
      <div className="c3-placeholder">
        <div className="ph-tag">C3 · dynamic interface</div>
        <div className="ph-title">The generated interface will mount here</div>
        <div className="help">
          This is the placeholder slot. In the C3 condition the model returns a small custom
          interface as JSX, and it is live-rendered inside this panel. It hasn’t been generated
          yet — drop a `jsx` string into the call-1 payload (or run the backend stub) and it
          appears here.
        </div>
        {fields.length > 0 && (
          <>
            <div className="help" style={{ marginTop: 10 }}>It will collect:</div>
            <ul className="ph-fields">{fields.map((f) => <li key={f.id}>{f.label}</li>)}</ul>
          </>
        )}
      </div>
      <div className="actions">
        <span className="spacer" />
        <button className="primary" onClick={proceed}>Show me the answer</button>
      </div>
    </div>
  );
}

export default function C3DynamicHost({ data, columns = [], onSubmit }) {
  const fieldsRef = React.useRef(data.fields || []);
  fieldsRef.current = data.fields || [];
  const onSubmitRef = React.useRef(onSubmit);
  onSubmitRef.current = onSubmit;
  const submitted = React.useRef(false);

  // Fully stable: depends on nothing, reads latest fields/onSubmit via refs. This keeps the
  // compiled component from remounting (and losing the participant's input) on parent renders.
  const submitResponses = React.useCallback((obj) => {
    if (submitted.current) return;
    submitted.current = true;
    const responses = (fieldsRef.current || [])
      .filter((f) => obj[f.id] !== undefined)
      .map((f) => ({ field_id: f.id, label: f.label, value: obj[f.id] }));
    onSubmitRef.current(responses, true); // compile_success = true
  }, []);

  const compiled = React.useMemo(() => {
    if (!data.jsx || !data.jsx.trim()) return { error: new Error("empty jsx") };
    try {
      return { Comp: buildComponent(data.jsx, submitResponses) };
    } catch (e) {
      return { error: e };
    }
  }, [data.jsx, submitResponses]);

  const fallback = <C3Fallback fields={data.fields || []} onSubmit={onSubmit} />;

  return (
    <SchemaColumnsContext.Provider value={columns}>
      {data.placeholder ? (
        <C3Placeholder fields={data.fields || []} onSubmit={onSubmit} />
      ) : compiled.error ? (
        fallback
      ) : (
        <ErrorBoundary fallback={fallback}>
          <compiled.Comp />
        </ErrorBoundary>
      )}
    </SchemaColumnsContext.Provider>
  );
}
