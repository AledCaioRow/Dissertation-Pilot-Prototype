/**
 * The participant wizard (build brief §3). A step-through state machine: one idea per
 * screen, Back where the brief allows it, a persistent footer from the study-explanation
 * screen onward, and incremental logging to the backend at every step.
 *
 * Flow: consent -> details -> study explanation -> author all four questions (locked
 * pre-interaction) -> interaction block 1 (condition by counterbalancing) -> questionnaire
 * -> interaction block 2 -> questionnaire -> debrief. Each interaction is: loading ->
 * interface -> interface-confidence -> (call 2 runs) -> output -> answer-confidence.
 */
import React from "react";
import { api } from "./api.js";
import copy from "./content/copy.json";

import ModeSelect from "./components/ModeSelect.jsx";
import ConsentDetails from "./components/ConsentDetails.jsx";
import Screening from "./components/Screening.jsx";
import StudyExplanation from "./components/StudyExplanation.jsx";
import QuestionAuthor from "./components/QuestionAuthor.jsx";
import LoadingScreen from "./components/LoadingScreen.jsx";
import C2StaticInterface from "./components/C2StaticInterface.jsx";
import C3DynamicHost from "./components/C3DynamicHost.jsx";
import ResultView from "./components/ResultView.jsx";
import PerceivedSuccess from "./components/PerceivedSuccess.jsx";
import SUS from "./components/SUS.jsx";
import AgencyItems from "./components/AgencyItems.jsx";
import Debrief from "./components/Debrief.jsx";
import { Footer } from "./components/ui.jsx";

// ============================================================
// DEV SKIP CONFIG
// Set SKIP_ALL = true to make every wizard phase skippable at
// once. Or set individual phase flags to true for finer control.
// A yellow "DEV: skip →" button appears at the top of each
// skippable screen. Default: all false (full participant flow).
// See README for documentation.
// ============================================================
const SKIP_ALL = false;
const SKIP_CONFIG = {
  mode:          SKIP_ALL,
  consent:       SKIP_ALL,
  screening:     SKIP_ALL,
  study:         SKIP_ALL,
  db_intro:      SKIP_ALL,
  author:        SKIP_ALL,
  loading:       SKIP_ALL,
  interface:     SKIP_ALL,
  iface_conf:    SKIP_ALL,
  output:        SKIP_ALL,
  ans_conf:      SKIP_ALL,
  questionnaire: SKIP_ALL,
  debrief:       SKIP_ALL,
};

const slotKey = (s) => `${s.database}:${s.ambiguity_class}`;
const qualifiedColumns = (schema) =>
  schema ? schema.tables.flatMap((t) => t.columns.map((c) => `${t.name}.${c.name}`)) : [];
const BACK_OK = new Set(["screening", "study", "db_intro", "author"]);

// Behaviour constants (the backend also exposes these via /config; kept simple here).
const loadingMinSeconds = 2;
const authMinChars = 15;

function buildScreens(assignment) {
  const screens = [{ type: "mode" }, { type: "consent" }, { type: "screening" }, { type: "study" }];
  let lastDb = null;
  assignment.authoring_plan.forEach((slot) => {
    if (slot.database !== lastDb) {
      screens.push({ type: "db_intro", db: slot.database });
      lastDb = slot.database;
    }
    screens.push({ type: "author", slot });
  });
  assignment.condition_block_order.forEach((cond) => {
    assignment.authoring_plan
      .filter((s) => s.condition === cond)
      .forEach((slot) => {
        screens.push({ type: "loading", slot });
        screens.push({ type: "interface", slot });
        screens.push({ type: "iface_conf", slot });
        screens.push({ type: "output", slot });
        screens.push({ type: "ans_conf", slot });
      });
    screens.push({ type: "questionnaire", condition: cond });
  });
  screens.push({ type: "debrief" }, { type: "final" });
  return screens;
}

export default function App() {
  const pid = React.useMemo(() => {
    const p = new URLSearchParams(window.location.search).get("pid");
    return p != null ? parseInt(p, 10) : Math.floor(Math.random() * 100000);
  }, []);

  const [assignment, setAssignment] = React.useState(null);
  const [useStub, setUseStub] = React.useState(true);   // page-0 choice (stub vs live)
  const [cfgStub, setCfgStub] = React.useState(true);   // backend default for page 0
  const [fatal, setFatal] = React.useState(null);
  const [withdrawn, setWithdrawn] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [index, setIndex] = React.useState(0);

  // Persistent participant data
  const [authored, setAuthored] = React.useState({}); // key -> {question, intent}
  const [trials, setTrials] = React.useState({});      // key -> {trial_id, condition}
  const [runtime, setRuntime] = React.useState({});    // trial_id -> {interface, columns, responses, compileSuccess, result, perceived}
  const [schemas, setSchemas] = React.useState({});    // db -> schema JSON
  const [qData, setQData] = React.useState({ C2: { sus: {}, agency: {}, open: {} }, C3: { sus: {}, agency: {}, open: {} } });
  const [debriefData, setDebriefData] = React.useState({});
  const [screening, setScreening] = React.useState({});

  const authoredRef = React.useRef(authored); authoredRef.current = authored;
  const trialsRef = React.useRef(trials); trialsRef.current = trials;
  const runtimeRef = React.useRef(runtime); runtimeRef.current = runtime;
  const schemaCacheRef = React.useRef({});

  React.useEffect(() => {
    (async () => {
      try {
        const cfg = await api.getConfig();
        setCfgStub(!!cfg.stubbed);
        setUseStub(!!cfg.stubbed);
        const r = await api.startSession(pid);
        setAssignment(r.assignment);
      } catch (e) {
        setFatal(
          "Couldn't reach the study backend. Make sure it's running (launch with " +
          "start.bat on Windows or ./start.sh on Mac/Linux), then reload this page."
        );
      }
    })();
  }, [pid]);

  const screens = React.useMemo(() => (assignment ? buildScreens(assignment) : []), [assignment]);
  const current = screens[index];

  // Prefetch the schema whenever a screen references a database.
  React.useEffect(() => {
    const db = current?.db || current?.slot?.database;
    if (db) loadSchema(db);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [index, current]);

  async function loadSchema(db) {
    if (schemaCacheRef.current[db]) return schemaCacheRef.current[db];
    const s = await api.getSchema(db);
    schemaCacheRef.current[db] = s;
    setSchemas({ ...schemaCacheRef.current });
    return s;
  }

  const next = () => setIndex((i) => i + 1);
  const back = () => setIndex((i) => Math.max(0, i - 1));
  const canBack = current && BACK_OK.has(current.type) && index > 0 && screens[index - 1].type !== "consent";

  // --- Author all four questions at the authoring->interaction boundary (locks intent). ---
  async function ensureTrials() {
    const map = { ...trialsRef.current };
    let changed = false;
    for (const slot of assignment.authoring_plan) {
      const key = slotKey(slot);
      if (!map[key]) {
        const a = authoredRef.current[key] || { question: "", intent: "" };
        const r = await api.author({
          participant_id: pid, db_name: slot.database, ambiguity_class: slot.ambiguity_class,
          question: a.question, intent_note: a.intent,
        });
        map[key] = { trial_id: r.trial_id, condition: r.condition };
        changed = true;
      }
    }
    if (changed) { trialsRef.current = map; setTrials(map); }
    return map;
  }

  const makeInterfaceTask = (slot) => async () => {
    const map = await ensureTrials();
    const t = map[slotKey(slot)];
    const schema = await loadSchema(slot.database);
    const iface = await api.trialInterface(pid, t.trial_id);
    return { trial_id: t.trial_id, condition: iface.condition, data: iface.data, columns: qualifiedColumns(schema) };
  };

  const onLoadingDone = (result) => {
    if (result?.error) { setFatal(result.error); return; }
    setRuntime((rt) => ({
      ...rt,
      [result.trial_id]: { ...(rt[result.trial_id] || {}), condition: result.condition, interface: result.data, columns: result.columns },
    }));
    next();
  };

  const onInterfaceSubmit = (trialId) => (responses, compileSuccess = null) => {
    setRuntime((rt) => ({ ...rt, [trialId]: { ...rt[trialId], responses, compileSuccess } }));
    next();
  };

  const setPerceived = (trialId) => (p) =>
    setRuntime((rt) => ({ ...rt, [trialId]: { ...rt[trialId], perceived: p } }));

  const onIfaceConfSubmit = (trialId) => async () => {
    setBusy(true);
    try {
      const t = runtimeRef.current[trialId];
      const ans = await api.trialAnswer({
        participant_id: pid, trial_id: trialId,
        responses: t.responses || [], compile_success: t.compileSuccess ?? null,
      });
      setRuntime((rt) => ({ ...rt, [trialId]: { ...rt[trialId], result: ans } }));
      next();
    } catch (e) { setFatal(String(e)); } finally { setBusy(false); }
  };

  const onAnsConfSubmit = (trialId) => async () => {
    try {
      const p = runtimeRef.current[trialId].perceived || {};
      await api.perceived({
        participant_id: pid, trial_id: trialId,
        interface_confidence: p.interface_confidence ?? null,
        answer_wanted: p.answer_wanted ?? null,
        answer_confidence: p.answer_confidence ?? null,
      });
      next();
    } catch (e) { setFatal(String(e)); }
  };

  const doWithdraw = async () => {
    try { await api.withdraw(pid); } catch (e) { /* mark locally regardless */ }
    setWithdrawn(true);
  };

  // Skip helper for the loading screen: synthesises interface data so downstream
  // screens (interface, output) have something to render without a real API call.
  const skipLoadingDirect = async (slot) => {
    try {
      const map = await ensureTrials();
      const t = map[slotKey(slot)];
      const schema = await loadSchema(slot.database);
      const syntheticData = t.condition === "C3"
        ? { jsx: "", fields: [], placeholder: true }
        : { widgets: [], allow_additional_constraints: false, placeholder: true };
      onLoadingDone({
        trial_id: t.trial_id,
        condition: t.condition,
        data: syntheticData,
        columns: qualifiedColumns(schema),
      });
    } catch (e) { setFatal(String(e)); }
  };

  // ---------------------------------------------------------------- render
  if (fatal) return <Shell><div className="screen error-box">Something went wrong: {fatal}</div></Shell>;
  if (withdrawn) return <Shell><div className="screen"><h1>{copy.withdrawn.heading}</h1><p>{copy.withdrawn.body}</p></div></Shell>;
  if (!assignment || !current) return <Shell><div className="screen center"><div className="loading-dots">• • •</div></div></Shell>;
  if (busy) return <Shell><div className="screen center"><h1>One moment</h1><div className="loading-dots">• • •</div></div></Shell>;

  let body = null;

  if (current.type === "mode") {
    body = <ModeSelect defaultUseStub={cfgStub} onSubmit={async (chosen) => {
      try { await api.setMode(pid, chosen); setUseStub(chosen); next(); }
      catch (e) { setFatal(String(e)); }
    }} />;

  } else if (current.type === "consent") {
    body = <ConsentDetails participantId={pid} onSubmit={async (payload) => {
      await api.consent({ participant_id: pid, ...payload }); next();
    }} />;

  } else if (current.type === "screening") {
    body = <Screening value={screening} onChange={setScreening}
      canBack={canBack} onBack={back}
      onSubmit={async () => { await api.screening({ participant_id: pid, ...screening }); next(); }} />;

  } else if (current.type === "study") {
    body = <StudyExplanation onNext={next} onBack={back} canBack={canBack} />;

  } else if (current.type === "db_intro") {
    const d = copy.db_intro[current.db];
    body = (
      <div className="screen">
        <h1>{d.heading}</h1>
        <p>{d.body}</p>
        <div className="actions">
          {canBack ? <button onClick={back}>{copy.nav.back}</button> : <span />}
          <span className="spacer" />
          <button className="primary" onClick={next}>{d.button}</button>
        </div>
      </div>
    );

  } else if (current.type === "author") {
    const key = slotKey(current.slot);
    body = <QuestionAuthor slot={current.slot} schema={schemas[current.slot.database]}
      value={authored[key]} minChars={authMinChars}
      onChange={(v) => setAuthored((a) => ({ ...a, [key]: v }))}
      canBack={canBack} onBack={back} onSubmit={next} />;

  } else if (current.type === "loading") {
    body = <LoadingScreen task={makeInterfaceTask(current.slot)} minSeconds={loadingMinSeconds} onDone={onLoadingDone} />;

  } else if (current.type === "interface") {
    const t = trials[slotKey(current.slot)];
    const rt = t ? (runtime[t.trial_id] || {}) : {};
    const trialId = t?.trial_id;
    const ifaceData = rt.interface || { placeholder: true, widgets: [], jsx: "", fields: [] };
    body = (
      <div className="screen">
        <p>{copy.interface.standing_instruction}</p>
        <div className="interface-panel">
          {rt.condition === "C3"
            ? <C3DynamicHost data={ifaceData} columns={rt.columns || []} onSubmit={trialId ? onInterfaceSubmit(trialId) : next} />
            : <C2StaticInterface data={ifaceData} onSubmit={trialId ? onInterfaceSubmit(trialId) : next} />}
        </div>
      </div>
    );

  } else if (current.type === "iface_conf") {
    const t = trials[slotKey(current.slot)];
    body = <PerceivedSuccess stage="interface" value={runtime[t?.trial_id]?.perceived || {}}
      onChange={t ? setPerceived(t.trial_id) : () => {}} onSubmit={t ? onIfaceConfSubmit(t.trial_id) : next} />;

  } else if (current.type === "output") {
    const t = trials[slotKey(current.slot)];
    const result = t ? runtime[t.trial_id]?.result : undefined;
    body = <ResultView result={result} onNext={next} />;

  } else if (current.type === "ans_conf") {
    const t = trials[slotKey(current.slot)];
    body = <PerceivedSuccess stage="answer" value={runtime[t?.trial_id]?.perceived || {}}
      onChange={t ? setPerceived(t.trial_id) : () => {}} onSubmit={t ? onAnsConfSubmit(t.trial_id) : next} />;

  } else if (current.type === "questionnaire") {
    const cond = current.condition;
    const q = qData[cond];
    const setSus = (sus) => setQData((d) => ({ ...d, [cond]: { ...d[cond], sus } }));
    const setAgency = (agency) => setQData((d) => ({ ...d, [cond]: { ...d[cond], agency } }));
    const setOpen = (i, val) => setQData((d) => ({ ...d, [cond]: { ...d[cond], open: { ...d[cond].open, [i]: val } } }));
    const ready = Object.keys(q.sus).length >= copy.questionnaire.sus_items.length
      && Object.keys(q.agency).length >= copy.questionnaire.agency_items.length;
    body = (
      <div className="screen">
        <h1>{copy.questionnaire.heading}</h1>
        <SUS value={q.sus} onChange={setSus} />
        <AgencyItems value={q.agency} onChange={setAgency} />
        <h2>{copy.questionnaire.open_intro}</h2>
        {copy.questionnaire.open_items.map((qq, i) => (
          <div key={i}><label>{qq}</label>
            <textarea value={q.open[i] || ""} onChange={(e) => setOpen(i, e.target.value)} /></div>
        ))}
        <div className="actions">
          <span className="spacer" />
          <button className="primary" disabled={!ready} onClick={async () => {
            await api.questionnaire({ participant_id: pid, condition: cond, sus: q.sus, agency: q.agency, open_ended: q.open });
            next();
          }}>{copy.questionnaire.button}</button>
        </div>
      </div>
    );

  } else if (current.type === "debrief") {
    body = <Debrief value={debriefData} onChange={setDebriefData} onSubmit={async () => {
      const open = {};
      copy.debrief.open_items.forEach((_, i) => (open[i] = debriefData[`open_${i}`] || ""));
      await api.debrief({ participant_id: pid, preference: debriefData.preference, open_ended: open });
      next();
    }} />;

  } else if (current.type === "final") {
    body = <div className="screen"><h1>Thank you</h1><p>{copy.debrief.final}</p></div>;
  }

  const showFooter = !["mode", "consent", "screening"].includes(current.type);

  // Determine the skip action for the current screen (null = no skip button shown).
  let skipAction = null;
  if (SKIP_CONFIG[current.type]) {
    if (current.type === "loading") {
      skipAction = () => skipLoadingDirect(current.slot);
    } else {
      skipAction = next;
    }
  }

  return (
    <Shell footer={showFooter ? <Footer onWithdraw={doWithdraw} /> : null} skipAction={skipAction}>
      {body}
    </Shell>
  );
}

function Shell({ children, footer, skipAction }) {
  return (
    <>
      <div className="wizard">
        {skipAction && (
          <div style={{ textAlign: "right", marginBottom: 6 }}>
            <button onClick={skipAction} style={{
              fontSize: "0.72rem", background: "#fffbe6", border: "1px solid #c8a600",
              borderRadius: 4, padding: "2px 10px", cursor: "pointer", color: "#5a4800",
              fontFamily: "inherit",
            }}>
              DEV: skip →
            </button>
          </div>
        )}
        {children}
      </div>
      {footer}
    </>
  );
}
