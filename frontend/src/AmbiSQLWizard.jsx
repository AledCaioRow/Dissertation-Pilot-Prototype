import { useState, useMemo, useRef } from "react";

/* =============================================================================
   AmbiSQLWizard  —  C2 (AmbiSQL-inspired) condition
   -----------------------------------------------------------------------------
   FIXED interface. The model NEVER writes UI here. It writes JSON (the spec),
   and this component renders one ambiguity at a time using a *polymorphic input
   slot* chosen by ambiguity.affordance. That polymorphism is the whole point:
   the taxonomy type maps to a control type, not just a label.

   Boundary:
     spec  (JSON in)  ->  <AmbiSQLWizard spec={spec} onComplete={fn} />
     log   (JSON out) ->  onComplete(log)

   ---- INPUT: AmbiguitySpec --------------------------------------------------
   {
     originalQuestion: string,
     databaseId: string,
     ambiguities: [{
       id: string,
       phrase: string,                 // the span in the question that is unclear
       type:  TaxonomyType,            // for logging + (optionally) the badge
       affordance: "choice" | "value" | "range" | "toggle" | "dateRange",
       clarificationQuestion: string,
       evidence: string,               // schema snippet / why this is ambiguous
       allowCustom: boolean,           // show the "other / custom" escape hatch
       // affordance-specific payload (only the relevant one is read):
       options?:  [{ value: string, label: string }],   // choice | value
       range?:    { min, max, step, unit },              // range
       toggle?:   { onLabel, offLabel },                 // toggle
       dateRange?:{ earliest: "YYYY-MM-DD", latest: "YYYY-MM-DD" }
     }]
   }

   TaxonomyType =
     "unclear_schema_reference" | "unclear_value_reference" | "missing_keyword" |
     "unclear_knowledge_source" | "insufficient_reasoning_context" |
     "conflicting_knowledge" | "ambiguous_temporal_spatial_scope"

   ---- OUTPUT: ResolutionLog -------------------------------------------------
   {
     originalQuestion, databaseId,
     resolutions: [{
       id, phrase, type, affordance, clarificationQuestion,
       optionsShown, selected, custom, skipped, timeMs
     }],
     rewrittenQuery,      // from call 2 (rewriteQuery)
     completedAt
   }
   ============================================================================= */

// ---- shared tokens (kept identical to StudyShell so the chrome matches) ----
const GREY = "#AEAEAE";
const TEAL = "#156082";
const LIGHT = "#E8E8E8";
const BLACK = "#000000";
const WHITE = "#FFFFFF";
const MUTE = "#5f6b70";
const FONT = "Arial, Helvetica, sans-serif";
const MONO = "'Courier New', ui-monospace, monospace";
const BORDER = `3px solid ${BLACK}`;

const TYPE_LABEL = {
  unclear_schema_reference: "unclear schema reference",
  unclear_value_reference: "unclear value reference",
  missing_keyword: "missing SQL keyword",
  unclear_knowledge_source: "unclear knowledge source",
  insufficient_reasoning_context: "insufficient reasoning context",
  conflicting_knowledge: "conflicting knowledge",
  ambiguous_temporal_spatial_scope: "ambiguous temporal / spatial scope",
};

/* ---------------------------------------------------------------------------
   DEMO_SPEC — lets the component render standalone and shows the polymorphism.
   In the study this is produced by call 1 (fetchAmbiguitySpec), not hard-coded.
   --------------------------------------------------------------------------- */
const DEMO_SPEC = {
  originalQuestion: "Which were the club's most successful events recently?",
  databaseId: "student_club",
  ambiguities: [
    {
      id: "amb_successful",
      phrase: "successful",
      type: "unclear_schema_reference",
      affordance: "choice",
      clarificationQuestion: "What should \u201csuccessful\u201d be measured by?",
      evidence: "event.attendance \u00b7 income.amount \u00b7 budget.spent vs budget.amount",
      allowCustom: true,
      options: [
        { value: "attendance", label: "Highest attendance" },
        { value: "income", label: "Most income raised" },
        { value: "profit", label: "Highest profit (income \u2212 spend)" },
        { value: "under_budget", label: "Stayed furthest under budget" },
      ],
    },
    {
      id: "amb_recently",
      phrase: "recently",
      type: "ambiguous_temporal_spatial_scope",
      affordance: "dateRange",
      clarificationQuestion: "Which dates count as \u201crecently\u201d?",
      evidence: "event.event_date ranges 2019-09-01 \u2192 2020-06-30",
      allowCustom: false,
      dateRange: { earliest: "2019-09-01", latest: "2020-06-30" },
    },
    {
      id: "amb_events_distinct",
      phrase: "events",
      type: "missing_keyword",
      affordance: "toggle",
      clarificationQuestion: "Should each event be counted once, even if it was held more than once?",
      evidence: "event has repeating names across event_date (e.g. \u201cWeekly Meeting\u201d \u00d712)",
      allowCustom: false,
      toggle: { onLabel: "Count each event once (DISTINCT)", offLabel: "Count every occurrence" },
    },
  ],
};

/* ---------------------------------------------------------------------------
   API HOOKS  —  the only two model calls. Same backend model for all 3
   conditions; what differs is the contract it must satisfy.

   Swap the mock bodies for your FastAPI endpoints (or the in-artifact
   Anthropic API). Keep the signatures so the component never changes.
   --------------------------------------------------------------------------- */

// CALL 1: detect + classify + choose affordance + pull options from the schema.
// The system prompt MUST constrain `affordance` to the enum and populate
// `options`/`range`/`dateRange` strictly from the real schema & values, or the
// UI stops being fixed.
export async function fetchAmbiguitySpec(question, databaseId) {
  // return fetch("/api/ambiguities", {
  //   method: "POST", headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ question, databaseId }),
  // }).then((r) => r.json());
  return Promise.resolve({ ...DEMO_SPEC, originalQuestion: question, databaseId });
}

// CALL 2: take the resolutions and rewrite the question into a clearer query.
// (Backend can also return the SQL + rows for the output stage.)
export async function rewriteQuery(question, resolutions, databaseId) {
  // return fetch("/api/rewrite", { ... }).then((r) => r.json());
  return Promise.resolve({ rewrittenQuery: assembleRewrite(question, resolutions) });
}

// Local placeholder rewrite so the prototype shows live progress without a server.
function assembleRewrite(question, resolutions) {
  let q = question;
  for (const r of resolutions) {
    if (r.skipped || (!r.selected && !r.custom)) continue;
    const answer = r.custom || labelFor(r);
    q = q.replace(r.phrase, `${r.phrase} [= ${answer}]`);
  }
  return q;
}
function labelFor(r) {
  const opt = (r.optionsShown || []).find((o) => o.value === r.selected);
  return opt ? opt.label : r.selected;
}

/* ===========================================================================
   COMPONENT
   =========================================================================== */
export default function AmbiSQLWizard({ spec = DEMO_SPEC, onComplete }) {
  const { originalQuestion, databaseId, ambiguities } = spec;

  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // id -> { selected, custom, skipped, timeMs }
  const [draftSelected, setDraftSelected] = useState(null);
  const [draftCustom, setDraftCustom] = useState("");
  const [finished, setFinished] = useState(false);
  const [finalLog, setFinalLog] = useState(null);
  const startRef = useRef(Date.now());

  const total = ambiguities.length;
  const amb = ambiguities[index];

  // running rewrite, built from whatever has been answered so far
  const resolutionsSoFar = useMemo(
    () => buildResolutions(ambiguities, answers),
    [ambiguities, answers]
  );
  const liveRewrite = useMemo(
    () => assembleRewrite(originalQuestion, resolutionsSoFar),
    [originalQuestion, resolutionsSoFar]
  );
  const anyAnswered = resolutionsSoFar.some((r) => !r.skipped && (r.selected || r.custom));

  function loadCard(i) {
    const prev = answers[ambiguities[i]?.id];
    setDraftSelected(prev?.selected ?? null);
    setDraftCustom(prev?.custom ?? "");
    startRef.current = Date.now();
  }

  function record(skip) {
    const timeMs = Date.now() - startRef.current;
    const next = {
      ...answers,
      [amb.id]: {
        selected: skip ? null : draftSelected,
        custom: skip ? "" : (draftCustom.trim() || ""),
        skipped: !!skip,
        timeMs,
      },
    };
    setAnswers(next);
    return next;
  }

  function go(skip) {
    const next = record(skip);
    if (index + 1 < total) {
      const ni = index + 1;
      setIndex(ni);
      loadCard(ni);
    } else {
      complete(next);
    }
  }

  async function complete(finalAnswers) {
    const resolutions = buildResolutions(ambiguities, finalAnswers);
    const { rewrittenQuery } = await rewriteQuery(originalQuestion, resolutions, databaseId);
    const log = {
      originalQuestion,
      databaseId,
      resolutions,
      rewrittenQuery,
      completedAt: new Date().toISOString(),
    };
    setFinalLog(log);
    setFinished(true);
    onComplete?.(log);
  }

  function jumpTo(i) {
    if (i === index || finished) return;
    record(false); // bank current card before jumping
    setIndex(i);
    loadCard(i);
  }

  // a card is "answerable" if something is chosen OR a custom value typed
  const canConfirm =
    draftSelected !== null || (amb.allowCustom && draftCustom.trim().length > 0);

  if (finished) return <Done log={finalLog} onComplete={onComplete} />;

  return (
    <Frame>
      {/* ---- the single active ambiguity card ---- */}
      <div style={card}>
        <div style={cardHead}>
          <span style={{ fontWeight: 700 }}>
            Ambiguity {index + 1} of {total}
          </span>
          <span style={badge}>{TYPE_LABEL[amb.type] || amb.type}</span>
        </div>

        <div style={{ fontSize: 16, marginBottom: 4 }}>
          Phrase: <span style={{ fontFamily: MONO, background: LIGHT, padding: "1px 6px" }}>
            "{amb.phrase}"
          </span>
        </div>
        <div style={{ fontSize: 18, fontWeight: 700, margin: "12px 0 12px" }}>
          {amb.clarificationQuestion}
        </div>

        {/* ---- polymorphic input slot: the control depends on affordance ---- */}
        <AffordanceSlot
          amb={amb}
          selected={draftSelected}
          onSelect={(v) => { setDraftSelected(v); }}
          custom={draftCustom}
          onCustom={(v) => { setDraftCustom(v); if (v) setDraftSelected(null); }}
        />

        {/* ---- evidence: why this is ambiguous ---- */}
        {amb.evidence && (
          <div style={evidence}>
            <span style={{ fontWeight: 700, color: BLACK }}>Why we're asking: </span>
            <span style={{ fontFamily: MONO }}>{amb.evidence}</span>
          </div>
        )}

        {/* ---- actions ---- */}
        <div style={{ display: "flex", gap: 12, marginTop: 16, alignItems: "center" }}>
          <button onClick={() => go(false)} disabled={!canConfirm} style={primaryBtn(canConfirm)}>
            {index + 1 < total ? "Confirm & next" : "Confirm & finish"}
          </button>
          <button onClick={() => go(true)} style={ghostBtn}>Skip this one</button>
          {index > 0 && (
            <button onClick={() => jumpTo(index - 1)} style={ghostBtn}>Back</button>
          )}
        </div>
      </div>

      {/* ---- running rewrite (progress, not a big bar) ---- */}
      {anyAnswered && (
        <div style={rewriteBox}>
          <div style={{ fontSize: 13, color: MUTE, marginBottom: 4 }}>Rewritten so far</div>
          <div style={{ fontFamily: MONO, fontSize: 15 }}>{liveRewrite}</div>
        </div>
      )}

      {/* ---- small ambiguity queue: chips, only one opens at a time ---- */}
      <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
        {ambiguities.map((a, i) => {
          const ans = answers[a.id];
          const state = i === index ? "active" : ans ? (ans.skipped ? "skipped" : "done") : "todo";
          return (
            <button key={a.id} onClick={() => jumpTo(i)} style={chip(state)} title={a.phrase}>
              <span style={{ fontWeight: 700 }}>
                {state === "done" ? "\u2713" : state === "skipped" ? "\u2013" : state === "active" ? "\u25cf" : i + 1}
              </span>
              <span style={{ fontSize: 11, opacity: 0.8 }}>{state}</span>
            </button>
          );
        })}
      </div>
    </Frame>
  );
}

/* ---------------------------------------------------------------------------
   The polymorphic input slot — one control per affordance, custom on all.
   --------------------------------------------------------------------------- */
function AffordanceSlot({ amb, selected, onSelect, custom, onCustom }) {
  const usingCustom = !!custom;
  return (
    <div style={{ display: "grid", gridTemplateColumns: amb.allowCustom ? "1.4fr 1fr" : "1fr", gap: 14 }}>
      <div style={slotBox}>
        <div style={slotLabel}>Suggested</div>
        {amb.affordance === "choice" && (
          <Choices options={amb.options} selected={usingCustom ? null : selected} onSelect={onSelect} />
        )}
        {amb.affordance === "value" && (
          <ValuePicker options={amb.options} selected={usingCustom ? null : selected} onSelect={onSelect} />
        )}
        {amb.affordance === "range" && (
          <RangePicker range={amb.range} value={usingCustom ? null : selected} onSelect={onSelect} />
        )}
        {amb.affordance === "toggle" && (
          <TogglePicker toggle={amb.toggle} selected={usingCustom ? null : selected} onSelect={onSelect} />
        )}
        {amb.affordance === "dateRange" && (
          <DateRangePicker dr={amb.dateRange} value={usingCustom ? null : selected} onSelect={onSelect} />
        )}
      </div>

      {amb.allowCustom && (
        <div style={slotBox}>
          <div style={slotLabel}>Other / custom</div>
          <input
            value={custom}
            onChange={(e) => onCustom(e.target.value)}
            placeholder="Describe what you mean…"
            style={input}
          />
          <div style={{ fontSize: 12, color: MUTE, marginTop: 8 }}>
            Typing here overrides the suggestions.
          </div>
        </div>
      )}
    </div>
  );
}

// affordance: choice  -> radio list
function Choices({ options = [], selected, onSelect }) {
  return (
    <div>
      {options.map((o) => (
        <label key={o.value} style={radioRow(selected === o.value)}>
          <input type="radio" checked={selected === o.value} onChange={() => onSelect(o.value)}
            style={{ width: 16, height: 16 }} />
          <span>{o.label}</span>
        </label>
      ))}
    </div>
  );
}

// affordance: value  -> dropdown of actual column values
function ValuePicker({ options = [], selected, onSelect }) {
  return (
    <select value={selected || ""} onChange={(e) => onSelect(e.target.value)} style={select}>
      <option value="" disabled>Choose a value…</option>
      {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}

// affordance: range  -> slider
function RangePicker({ range, value, onSelect }) {
  const { min = 0, max = 100, step = 1, unit = "" } = range || {};
  const v = value === null || value === undefined ? Math.round((min + max) / 2) : Number(value);
  return (
    <div>
      <input type="range" min={min} max={max} step={step} value={v}
        onChange={(e) => onSelect(e.target.value)} style={{ width: "100%" }} />
      <div style={{ fontFamily: MONO, marginTop: 6 }}>{v}{unit ? ` ${unit}` : ""}</div>
    </div>
  );
}

// affordance: toggle -> two-state segmented (e.g. DISTINCT yes/no)
function TogglePicker({ toggle, selected, onSelect }) {
  const opts = [
    { value: "on", label: toggle?.onLabel || "Yes" },
    { value: "off", label: toggle?.offLabel || "No" },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {opts.map((o) => (
        <button key={o.value} onClick={() => onSelect(o.value)} style={segBtn(selected === o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

// affordance: dateRange -> two date inputs encoded as "start..end"
function DateRangePicker({ dr, value, onSelect }) {
  const [start, end] = (value || "..").split("..");
  const set = (s, e) => onSelect(`${s || ""}..${e || ""}`);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 15 }}>
      <label style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <span>From</span>
        <input type="date" min={dr?.earliest} max={dr?.latest} value={start || ""}
          onChange={(e) => set(e.target.value, end)} style={dateInput} />
      </label>
      <label style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <span>To</span>
        <input type="date" min={dr?.earliest} max={dr?.latest} value={end || ""}
          onChange={(e) => set(start, e.target.value)} style={dateInput} />
      </label>
    </div>
  );
}

/* ---- completion screen (hands the log to the output stage) ---- */
function Done({ log, onComplete }) {
  return (
    <Frame>
      <div style={card}>
        <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 10 }}>All ambiguities handled.</div>
        <div style={{ fontSize: 13, color: MUTE, marginBottom: 4 }}>Clarified query sent to the output stage:</div>
        <div style={{ fontFamily: MONO, fontSize: 16, background: LIGHT, padding: 12, border: BORDER }}>
          {log.rewrittenQuery}
        </div>
        <div style={{ fontSize: 12, color: MUTE, marginTop: 12 }}>
          {log.resolutions.filter((r) => !r.skipped).length} of {log.resolutions.length} resolved
          {" \u00b7 "}
          logged for analysis
        </div>
      </div>
    </Frame>
  );
}

/* ---- helpers ---- */
function buildResolutions(ambiguities, answers) {
  return ambiguities.map((a) => {
    const ans = answers[a.id] || {};
    return {
      id: a.id,
      phrase: a.phrase,
      type: a.type,
      affordance: a.affordance,
      clarificationQuestion: a.clarificationQuestion,
      optionsShown: a.options || null,
      selected: ans.selected ?? null,
      custom: ans.custom || "",
      skipped: !!ans.skipped,
      timeMs: ans.timeMs ?? null,
    };
  });
}

/* ---- layout + style ---- */
function Frame({ children }) {
  return (
    <div style={{
      fontFamily: FONT, color: BLACK, background: GREY, height: "100%",
      padding: 22, boxSizing: "border-box", overflowY: "auto",
    }}>
      <div style={{ maxWidth: 720, margin: "0 auto" }}>{children}</div>
    </div>
  );
}

const card = { background: WHITE, border: BORDER, padding: 22 };
const cardHead = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 };
const badge = { fontSize: 12, fontFamily: MONO, color: WHITE, background: TEAL, padding: "3px 8px", letterSpacing: 0.3 };
const slotBox = { border: `2px solid ${BLACK}`, padding: 12 };
const slotLabel = { fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: MUTE, marginBottom: 8 };
const evidence = { marginTop: 14, fontSize: 13, color: MUTE, background: LIGHT, padding: "8px 10px", borderLeft: `4px solid ${TEAL}` };
const rewriteBox = { marginTop: 14, background: WHITE, border: `2px dashed ${MUTE}`, padding: "10px 12px" };
const input = { width: "100%", padding: "10px 12px", fontFamily: FONT, fontSize: 15, border: BORDER, borderRadius: 0, boxSizing: "border-box" };
const select = { width: "100%", padding: "10px 12px", fontFamily: FONT, fontSize: 15, border: BORDER, borderRadius: 0, background: WHITE, boxSizing: "border-box" };
const dateInput = { padding: "6px 8px", fontFamily: FONT, fontSize: 14, border: `2px solid ${BLACK}`, borderRadius: 0 };

function radioRow(active) {
  return { display: "flex", alignItems: "center", gap: 10, padding: "7px 8px", marginBottom: 4,
    fontSize: 15, cursor: "pointer", background: active ? "#e9f1f5" : "transparent", border: active ? `2px solid ${TEAL}` : "2px solid transparent" };
}
function segBtn(active) {
  return { textAlign: "left", padding: "10px 12px", fontFamily: FONT, fontSize: 15, cursor: "pointer", borderRadius: 0,
    border: BORDER, background: active ? TEAL : WHITE, color: active ? WHITE : BLACK, fontWeight: active ? 700 : 400 };
}
function primaryBtn(enabled) {
  return { padding: "11px 22px", fontFamily: FONT, fontSize: 16, fontWeight: 700, borderRadius: 0, border: BORDER,
    background: enabled ? TEAL : "#9bb6c1", color: WHITE, cursor: enabled ? "pointer" : "default" };
}
const ghostBtn = { padding: "11px 16px", fontFamily: FONT, fontSize: 15, borderRadius: 0, border: BORDER, background: WHITE, color: BLACK, cursor: "pointer" };
function chip(state) {
  const bg = state === "active" ? TEAL : state === "done" ? "#2f7d4f" : state === "skipped" ? "#9a9a9a" : WHITE;
  const fg = state === "todo" ? BLACK : WHITE;
  return { display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    width: 64, height: 48, border: BORDER, borderRadius: 0, background: bg, color: fg, cursor: "pointer", fontFamily: FONT };
}
