import { useEffect, useMemo, useRef, useState } from "react";
import { postJSON } from "../lib/api.js";

// React + Babel are bundled LOCALLY (imported as raw text) and injected into the
// sandboxed iframe — never fetched from a CDN, so the generated code cannot phone
// home (CSP connect-src 'none').
import reactSrc from "../sandbox/vendor/react.production.min.js?raw";
import reactDomSrc from "../sandbox/vendor/react-dom.production.min.js?raw";
import babelSrc from "../sandbox/vendor/babel.min.js?raw";

// C3 — Dynamic. Mounts the model-written Clarifier component (from /api/dynamic)
// inside a sandboxed iframe (sandbox="allow-scripts", NO allow-same-origin), with
// a strict CSP. Communication is validated postMessage only:
//   parent -> iframe: { type:"init", question, ambiguities, componentSrc }
//   iframe -> parent: { type:"ready" | "rendered" | "log" | "resolve" | "error" }
// On error or timeout we fall back to a minimal form so the person is never stuck.

const BLACK = "#000000";
const WHITE = "#FFFFFF";
const TEAL = "#156082";
const LIGHT = "#E8E8E8";
const FONT = "Arial, Helvetica, sans-serif";
const BORDER = `3px solid ${BLACK}`;

const RENDER_TIMEOUT_MS = 12000;

// The static iframe shell. The component source arrives at runtime via init.
function buildSrcDoc() {
  const csp =
    "default-src 'none'; " +
    "script-src 'unsafe-inline' 'unsafe-eval'; " +
    "style-src 'unsafe-inline'; " +
    "img-src data:; " +
    "connect-src 'none'; " +
    "form-action 'none'; " +
    "base-uri 'none'";
  return `<!doctype html><html><head>
<meta charset="utf-8" />
<meta http-equiv="Content-Security-Policy" content="${csp}" />
<style>
  html,body{margin:0;font-family:${FONT};color:${BLACK};background:${WHITE};}
  #root{padding:16px;box-sizing:border-box;width:100%;}
  *{box-sizing:border-box;}
</style>
</head><body>
<div id="root"></div>
<script>${reactSrc}<\/script>
<script>${reactDomSrc}<\/script>
<script>${babelSrc}<\/script>
<script>
(function(){
  "use strict";
  var post = function(msg){ parent.postMessage(msg, "*"); };
  var rootEl = document.getElementById("root");
  var rendered = false;

  function ErrorBoundaryFactory(React){
    return class EB extends React.Component {
      constructor(p){ super(p); this.state={err:null}; }
      static getDerivedStateFromError(e){ return {err: String(e && e.message || e)}; }
      componentDidCatch(e){ post({type:"error", message: String(e && e.message || e)}); }
      render(){
        if(this.state.err){ return React.createElement("div",{style:{color:"#7a1f1f"}},"This interface hit an error."); }
        return this.props.children;
      }
    };
  }

  function boot(init){
    try{
      if(!window.React || !window.ReactDOM || !window.Babel){
        post({type:"error", message:"libraries failed to load"}); return;
      }
      var React = window.React;
      var logEvent = function(type, payload){ post({type:"log", event:{type:type, payload:payload}}); };
      var resolved = false;
      var onResolve = function(resolutions){
        if(resolved) return; resolved = true;
        post({type:"resolve", resolutions: resolutions});
      };
      // expose the host-provided context to the component as globals
      window.QUESTION = init.question;
      window.AMBIGUITIES = init.ambiguities || [];

      var compiled = window.Babel.transform(init.componentSrc, {presets:["react"]}).code;
      var factory = new Function("React","onResolve","logEvent","question","ambiguities",
        compiled + "\\n return Clarifier;");
      var Clarifier = factory(React, onResolve, logEvent, init.question, init.ambiguities || []);
      if(typeof Clarifier !== "function"){ post({type:"error", message:"no Clarifier component"}); return; }
      var EB = ErrorBoundaryFactory(React);
      var root = window.ReactDOM.createRoot(rootEl);
      root.render(React.createElement(EB, null, React.createElement(Clarifier)));
      rendered = true;
      post({type:"rendered"});
    }catch(e){
      post({type:"error", message: String(e && e.message || e)});
    }
  }

  window.addEventListener("message", function(ev){
    var d = ev.data;
    if(!d || typeof d !== "object") return;
    if(d.type === "init" && !rendered){ boot(d); }
  });
  post({type:"ready"});
})();
<\/script>
</body></html>`;
}

export default function DynamicHost({ sessionId, questionIndex, question, ambiguities, componentSrc, contractVersion, onResolve, onLog }) {
  const iframeRef = useRef(null);
  const [mode, setMode] = useState("loading"); // loading | live | fallback
  const reported = useRef(false);
  const srcDoc = useMemo(buildSrcDoc, []);

  // Report render outcome to the backend exactly once.
  const reportStatus = (rendered_ok, used_fallback) => {
    if (reported.current) return;
    reported.current = true;
    postJSON("/api/dynamic-status", {
      session_id: sessionId, question_index: questionIndex,
      component_src: componentSrc || "", contract_version: contractVersion,
      rendered_ok, used_fallback,
    }).catch(() => {});
  };

  useEffect(() => {
    let timer = null;
    function onMessage(ev) {
      // Validate: must come from OUR iframe's window.
      if (!iframeRef.current || ev.source !== iframeRef.current.contentWindow) return;
      const d = ev.data;
      if (!d || typeof d !== "object") return;
      switch (d.type) {
        case "ready":
          // iframe shell is up; hand it the component source + context.
          ev.source.postMessage(
            { type: "init", question, ambiguities: ambiguities || [], componentSrc },
            "*"
          );
          break;
        case "rendered":
          if (timer) clearTimeout(timer);
          setMode("live");
          onLog?.("dynamic_rendered", { value: { contract: contractVersion } });
          reportStatus(true, false);
          break;
        case "log":
          onLog?.("dynamic_interaction", { value: d.event });
          break;
        case "resolve":
          if (Array.isArray(d.resolutions)) {
            onLog?.("dynamic_resolve", { value: { count: d.resolutions.length } });
            onResolve(d.resolutions);
          }
          break;
        case "error":
          if (timer) clearTimeout(timer);
          onLog?.("dynamic_error", { value: { message: String(d.message).slice(0, 300) } });
          setMode("fallback");
          reportStatus(false, true);
          break;
        default:
          break;
      }
    }
    window.addEventListener("message", onMessage);
    // Timeout → fallback if the component never reports "rendered".
    timer = setTimeout(() => {
      setMode((m) => {
        if (m === "loading") {
          onLog?.("dynamic_fallback", { value: { reason: "timeout" } });
          reportStatus(false, true);
          return "fallback";
        }
        return m;
      });
    }, RENDER_TIMEOUT_MS);
    return () => { window.removeEventListener("message", onMessage); if (timer) clearTimeout(timer); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (mode === "fallback") {
    return (
      <FallbackForm
        question={question}
        ambiguities={ambiguities || []}
        onResolve={onResolve}
        onLog={onLog}
      />
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 8 }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, margin: 0, color: BLACK }}>Clarify your question</h1>
      <div style={{ flex: "1 1 auto", minHeight: 0, border: BORDER, background: WHITE, position: "relative" }}>
        {mode === "loading" && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT, color: BLACK }}>
            Loading the interface…
          </div>
        )}
        <iframe
          ref={iframeRef}
          title="dynamic-clarifier"
          sandbox="allow-scripts"
          srcDoc={srcDoc}
          style={{ width: "100%", height: "100%", border: "none", display: "block" }}
        />
      </div>
    </div>
  );
}

// Minimal "what did you mean by X?" form — the mandatory safety net.
function FallbackForm({ question, ambiguities, onResolve, onLog }) {
  const items = ambiguities.length
    ? ambiguities
    : [{ id: "whole", phrase: question, clarificationQuestion: "Add anything that would make your question clearer." }];
  const [vals, setVals] = useState({});
  const [skips, setSkips] = useState({});

  useEffect(() => { onLog?.("dynamic_fallback", { value: { shown: true } }); }, []); // eslint-disable-line

  const finish = () => {
    const resolutions = items.map((a) => ({
      id: a.id, phrase: a.phrase,
      clarificationQuestion: a.clarificationQuestion,
      selected: null,
      custom: skips[a.id] ? "" : (vals[a.id] || "").trim(),
      skipped: !!skips[a.id],
    }));
    onResolve(resolutions);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 12, color: BLACK }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Clarify your question</h1>
      <div style={{ fontSize: 14, color: "#5f6b70" }}>
        A simple form is shown so you can still continue.
      </div>
      <div style={{ flex: "1 1 auto", minHeight: 0, overflowY: "auto", border: BORDER, background: WHITE, padding: 16 }}>
        {items.map((a) => (
          <div key={a.id} style={{ marginBottom: 18 }}>
            <div style={{ fontSize: 15, marginBottom: 4 }}>
              What did you mean by <b>“{a.phrase}”</b>?
            </div>
            {a.clarificationQuestion && (
              <div style={{ fontSize: 13, color: "#5f6b70", marginBottom: 6 }}>{a.clarificationQuestion}</div>
            )}
            <input
              value={vals[a.id] || ""}
              disabled={!!skips[a.id]}
              onChange={(e) => { setVals((v) => ({ ...v, [a.id]: e.target.value })); onLog?.("dynamic_interaction", { value: { fallback_type: a.id } }); }}
              placeholder="Type your answer…"
              style={{ width: "100%", padding: "10px 12px", fontFamily: FONT, fontSize: 15, border: BORDER, borderRadius: 0, boxSizing: "border-box", background: skips[a.id] ? LIGHT : WHITE }}
            />
            <label style={{ fontSize: 13, display: "inline-flex", gap: 6, marginTop: 6, alignItems: "center" }}>
              <input type="checkbox" checked={!!skips[a.id]} onChange={(e) => setSkips((s) => ({ ...s, [a.id]: e.target.checked }))} />
              Skip this one
            </label>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button onClick={finish} style={{ padding: "11px 24px", background: TEAL, color: WHITE, border: BORDER, fontFamily: FONT, fontSize: 16, fontWeight: 700, cursor: "pointer", borderRadius: 0 }}>
          Get my answer →
        </button>
      </div>
    </div>
  );
}
