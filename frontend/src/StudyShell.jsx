import { useState } from "react";

// ---- Design tokens (matched to the PowerPoint mockup) ----
const GREY = "#AEAEAE";   // page background
const TEAL = "#156082";   // panels / boxes
const LIGHT = "#E8E8E8";  // consent panel
const BLACK = "#000000";
const WHITE = "#FFFFFF";
const FONT = "Arial, Helvetica, sans-serif";
const BORDER = `3px solid ${BLACK}`;

const SCREENS = [
  "welcome",
  "consent",
  "demographics",
  "whatdoing",
  "guidance",
  "task",
  "interface-1", "output-1", "feedback-1",
  "interface-2", "output-2", "feedback-2",
  "interface-3", "output-3", "feedback-3",
  "end",
];

const TASK_INDEX = SCREENS.indexOf("task");

// ---- Shared bits ----
function Panel({ children, style }) {
  return (
    <div style={{ background: TEAL, color: WHITE, border: BORDER, padding: 24, ...style }}>
      {children}
    </div>
  );
}

function ArrowButton({ dir, onClick }) {
  return (
    <button
      onClick={onClick}
      aria-label={dir === "back" ? "Back" : "Forward"}
      style={{
        width: 84, height: 52, background: WHITE, border: BORDER,
        fontFamily: FONT, fontSize: 30, lineHeight: 1, cursor: "pointer",
        color: BLACK, borderRadius: 0,
      }}
    >
      {dir === "back" ? "\u2190" : "\u2192"}
    </button>
  );
}

function BlankSlot({ label }) {
  return (
    <div style={{ flex: 1, position: "relative", background: TEAL, border: BORDER }}>
      <span style={{
        position: "absolute", top: 10, left: 14, fontFamily: FONT,
        fontSize: 13, letterSpacing: 1, color: "rgba(255,255,255,0.55)",
        textTransform: "uppercase",
      }}>
        {label}
      </span>
    </div>
  );
}

const LIKERT = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"];

function LikertRow({ prompt, value, onChange }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ fontSize: 16, marginBottom: 8 }}>{prompt}</div>
      <div style={{ display: "flex", gap: 8, alignItems: "stretch" }}>
        {LIKERT.map((label, i) => {
          const selected = value === i;
          return (
            <button
              key={i}
              onClick={() => onChange(i)}
              style={{
                flex: 1, padding: "8px 6px", fontFamily: FONT, fontSize: 13,
                cursor: "pointer", borderRadius: 0, border: BORDER,
                background: selected ? TEAL : WHITE,
                color: selected ? WHITE : BLACK, fontWeight: selected ? 700 : 400,
              }}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ---- The database description (left scrollable panel) ----
function ClubRecords() {
  const h = { fontSize: 19, fontWeight: 700, margin: "18px 0 6px" };
  const li = { marginBottom: 6, lineHeight: 1.4 };
  const ul = { margin: "0 0 6px", paddingLeft: 24, listStyleType: "disc" };
  return (
    <div style={{ fontSize: 16, lineHeight: 1.45 }}>
      <div style={{ fontSize: 22, fontWeight: 700, textAlign: "center", marginBottom: 10 }}>
        The Student Club Records
      </div>
      <p style={{ margin: "0 0 8px" }}>
        These records describe one university club across the 2019–20 academic year. It
        contains the people who belong to it, the events it ran, and the money it handled.
        Here is the information they hold about each:
      </p>

      <div style={h}>The members</div>
      <p style={{ margin: "0 0 4px" }}>For every person in the club, the records hold:</p>
      <ul style={ul}>
        <li style={li}>their <b>full name</b></li>
        <li style={li}>their <b>email address</b> and their <b>phone number</b> to reach them on</li>
        <li style={li}>the <b>role they hold</b> in the club. Roles include: an ordinary member, an inactive member, or an officer such as President, Vice President, Treasurer or Secretary.</li>
        <li style={li}>their <b>T-shirt size</b>, from Small up to X-Large, for when shirts are ordered</li>
        <li style={li}>the <b>subject they study</b> (their course) and the department and college it sits in</li>
        <li style={li}>where they are <b>from</b> — a home postcode, which gives their town, county and state</li>
      </ul>

      <div style={h}>The events</div>
      <p style={{ margin: "0 0 4px" }}>For each event the club ran or planned, the records hold:</p>
      <ul style={ul}>
        <li style={li}>its <b>name</b> and the <b>date</b> (for example, “Spring Elections,” held one morning in March)</li>
        <li style={li}>what <b>kind</b> of event it was (a meeting, a game, a social, an election, a guest speaker, a registration session or community service)</li>
        <li style={li}>where it was <b>held</b> — the venue and/or address</li>
        <li style={li}>its <b>status</b> (finished/closed, currently open, or still being planned)</li>
        <li style={li}>additional extra <b>notes</b> the organisers left</li>
        <li style={li}>which <b>members turned up</b> to each event, so you can see how many attended</li>
      </ul>

      <div style={h}>The money</div>
      <p style={{ margin: "0 0 4px" }}>The club’s finances separate into three parts: budget, bills and income.</p>
      <p style={{ margin: "8px 0 4px" }}><i>The budget.</i> For each event, money is set aside by category (food, advertising, parking, speaker gifts, club T-shirts). For each one the records show:</p>
      <ul style={ul}>
        <li style={li}>how much was set aside for it</li>
        <li style={li}>how much has been spent so far</li>
        <li style={li}>how much is left</li>
      </ul>
      <p style={{ margin: "8px 0 4px" }}><i>The bills.</i> Each real cost the club paid records:</p>
      <ul style={ul}>
        <li style={li}>what the money was spent on, with its cost and date — say, pizza for $124 or club shirts for $295</li>
        <li style={li}>who paid it, and whether it was approved (true or false)</li>
      </ul>
      <p style={{ margin: "8px 0 4px" }}><i>The income.</i> Each sum of money received records:</p>
      <ul style={{ ...ul, marginBottom: 0 }}>
        <li style={li}>the amount and the date received</li>
        <li style={li}>where it came from — membership dues, the university’s annual allocation, fundraising, or sponsorship</li>
        <li style={li}>who handled it, plus any notes</li>
      </ul>
    </div>
  );
}

function QuestionGuidance() {
  const li = { marginBottom: 12, lineHeight: 1.5 };
  return (
    <div style={{ fontSize: 16, lineHeight: 1.5 }}>
      <p style={{ margin: "0 0 12px" }}>
        After reading all the info on this page and the next page, we’d like you to write
        three questions that could be answered from the information provided. Write them as if
        you are someone trying to find out something specific, so your intention is clear. The
        next page explains the data that you’ll be asking questions about. When reading the
        data about a student club on the next page, please bear in mind that we’re testing how
        well an AI can understand a question and fetch the information you’re actually after,
        so to challenge it we’d prefer questions that are challenging rather than simpler ones
        such as “show all the students.”
      </p>
      <p style={{ margin: "0 0 8px" }}>A challenging question does at least one of these four things:</p>
      <ol style={{ margin: 0, paddingLeft: 24, listStyleType: "decimal" }}>
        <li style={li}><b>It could mean more than one thing.</b> Example: “Which were the club’s most successful events?” The word successful might mean the best attended, the ones that raised the most money, or the ones that stayed within budget.</li>
        <li style={li}><b>It combines more than one kind of information,</b> drawing on at least two of these three: people, events, and money. Example: “Which members paid for something at an event they also attended?”</li>
        <li style={li}><b>It involves working something out,</b> not just reading off a fact. The answer might come from adding figures up, finding an average, or comparing one group against another. Example: “Do socials or meetings draw a bigger turnout on average?” The answer comes from looking at how many people went to each event and then comparing the two types.</li>
        <li style={li}><b>It leaves a specific detail unstated.</b> Somewhere in your question there is a missing boundary, such as a time frame, a place, or a cutoff, and a value has to be settled before it can be answered. Example: “How much did we spend in the early weeks of term?” It is clear that you want a spending total. What is not clear is exactly which weeks should be treated as early.</li>
      </ol>
    </div>
  );
}

// ---- Main ----
export default function StudyShell() {
  const [index, setIndex] = useState(0);
  const [exited, setExited] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [submitted, setSubmitted] = useState(0); // questions submitted on task screen
  const [draft, setDraft] = useState("");
  const [demographics, setDemographics] = useState({ age: "", exp: "", freq: "" });
  const [feedback, setFeedback] = useState({}); // { "feedback-1": {q1, q2, text} }

  const screen = SCREENS[index];
  const isLast = index === SCREENS.length - 1;
  // Back: shown after the first screen, but removed once 3 questions are submitted
  // (i.e. for the whole post-task phase) and never beyond the task screen.
  const showBack = index >= 1 && index <= TASK_INDEX && submitted < 3;
  const showForward = !isLast;

  const goBack = () => setIndex((i) => Math.max(0, i - 1));
  const goForward = () => setIndex((i) => Math.min(SCREENS.length - 1, i + 1));

  const submitQuestion = () => {
    setSubmitted((s) => {
      const next = Math.min(3, s + 1);
      return next;
    });
    setDraft("");
  };

  // ----- Screen content -----
  const Centered = ({ children }) => (
    <div style={{ maxWidth: 920, margin: "0 auto", fontSize: 22, lineHeight: 1.5, textAlign: "center" }}>
      {children}
    </div>
  );

  function renderScreen() {
    switch (screen) {
      case "welcome":
        return (
          <Centered>
            <p>
              Thank you for taking part. This study looks at how AI–human interactions could
              be supported by user design to get information out of a database. We wish to see
              if AI can help individuals who do not know databases to get the information they
              need, even if the request is vague.
            </p>
            <p>
              Please allow 10–15 minutes to take the study, and please be in a quiet room
              without distractions. There is a button below to exit at any moment if you
              change your mind about participating.
            </p>
          </Centered>
        );

      case "consent":
        return (
          <div style={{ maxWidth: 1000, margin: "0 auto" }}>
            <h1 style={{ textAlign: "center", fontSize: 36, fontWeight: 700, margin: "0 0 20px" }}>
              Consent Confirmation
            </h1>
            <div style={{ background: LIGHT, border: BORDER, padding: 28, color: BLACK }}>
              {[
                "I confirm I have read and understood the information sheet.",
                "I understand my participation is voluntary and I may stop at any time, including asking for my session recording to be deleted, without giving a reason.",
                "I understand the session will be audio-recorded and that my data will be stored securely and anonymised.",
                "I agree to take part.",
              ].map((t, i) => (
                <label key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start", fontSize: 18, marginBottom: 16, lineHeight: 1.4 }}>
                  <input type="checkbox" style={{ marginTop: 5, width: 18, height: 18 }} />
                  <span>{t}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case "demographics": {
        const set = (k) => (e) => setDemographics((d) => ({ ...d, [k]: e.target.value }));
        const selStyle = { width: "100%", padding: "8px 12px", fontFamily: FONT, fontSize: 15, border: BORDER, borderRadius: 0, background: WHITE, marginBottom: 14, boxSizing: "border-box" };
        const q = { fontSize: 16, fontWeight: 700, marginBottom: 6 };
        return (
          <div style={{ maxWidth: 1000, margin: "0 auto", width: "100%" }}>
            <p style={{ fontSize: 16, marginBottom: 12 }}>
              Before we start, a few questions where there is no bad answer. It is just useful
              to have this info.
            </p>
            <div style={{ background: WHITE, border: BORDER, padding: 18, color: BLACK }}>
              <div style={q}>Which age band are you in?</div>
              <select value={demographics.age} onChange={set("age")} style={selStyle}>
                <option value="">Choose…</option>
                {["18–24", "25–34", "35–44", "45–54", "55–64", "65+", "Prefer not to say"].map((o) => <option key={o}>{o}</option>)}
              </select>
              <div style={q}>How much experience do you have writing database queries (for example SQL)?</div>
              <select value={demographics.exp} onChange={set("exp")} style={selStyle}>
                <option value="">Choose…</option>
                {["None", "A little", "Moderate", "A lot", "Expert"].map((o) => <option key={o}>{o}</option>)}
              </select>
              <div style={q}>How often do you work with databases or spreadsheets of records?</div>
              <select value={demographics.freq} onChange={set("freq")} style={{ ...selStyle, marginBottom: 0 }}>
                <option value="">Choose…</option>
                {["Never", "Rarely", "Sometimes", "Often", "Daily"].map((o) => <option key={o}>{o}</option>)}
              </select>
            </div>
          </div>
        );
      }

      case "whatdoing":
        return (
          <div style={{ maxWidth: 1000, margin: "0 auto", width: "100%" }}>
            <h1 style={{ fontSize: 28, fontWeight: 700, margin: "0 0 14px" }}>What you’ll be doing</h1>
            <div style={{ fontSize: 17, lineHeight: 1.45 }}>
              <p style={{ margin: "0 0 10px" }}>
                You will look at one database. You will first be given information about what
                the database contains and what kind of questions it can help answer.
              </p>
              <p style={{ margin: "0 0 10px" }}>
                After reading this information, you will write three questions that you would
                like answered from the database. These should be questions you are genuinely
                interested in, written in your own words. There are no right or wrong questions.
              </p>
              <p style={{ margin: 0 }}>
                You will then receive responses to your questions, each through a different
                interface (a text response, and two differently designed user interfaces). The
                interface is there to help the AI understand your question and reduce issues
                such as vagueness, unclear wording, or the question not being answerable.
              </p>
            </div>
          </div>
        );

      case "guidance":
        return (
          <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14 }}>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>
              A note about writing your questions
            </h1>
            <div style={{
              flex: "1 1 auto", minHeight: 0, background: WHITE, color: BLACK,
              border: BORDER, padding: 24, overflowY: "auto", boxSizing: "border-box",
            }}>
              <QuestionGuidance />
            </div>
          </div>
        );

      case "task": {
        const done = submitted >= 3;
        return (
          <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14 }}>
            <h1 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>
              Please read all the contents of this page carefully
            </h1>
            {/* single full-width box holding the data; scrolls internally (page stays static) */}
            <div style={{
              flex: "1 1 auto", minHeight: 0, background: WHITE, color: BLACK,
              border: BORDER, padding: 22, overflowY: "scroll", boxSizing: "border-box",
            }}>
              <ClubRecords />
            </div>
            {/* submit area: full width, below the box */}
            <div style={{ flex: "0 0 auto" }}>
              <div style={{ color: BLACK, fontSize: 17, marginBottom: 10 }}>
                Please read the above and then submit three different questions. Remember: each
                question should be somewhat challenging.{" "}
                <span style={{ fontWeight: 700 }}>
                  {done ? "All 3 submitted — press → to continue." : `Question ${submitted + 1} of 3`}
                </span>
              </div>
              <div style={{ display: "flex", gap: 12, alignItems: "stretch" }}>
                <input
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  disabled={done}
                  placeholder="Type your question here (optional — you can skip)…"
                  style={{ flex: 1, padding: "14px 16px", fontFamily: FONT, fontSize: 17, border: BORDER, borderRadius: 0, background: done ? LIGHT : WHITE, boxSizing: "border-box" }}
                />
                <button
                  onClick={submitQuestion}
                  disabled={done}
                  style={{ padding: "0 32px", background: done ? "#5a7d91" : TEAL, color: WHITE, border: BORDER, fontFamily: FONT, fontSize: 17, fontWeight: 700, cursor: done ? "default" : "pointer", borderRadius: 0 }}
                >
                  Submit
                </button>
              </div>
            </div>
          </div>
        );
      }

      case "interface-1":
      case "interface-2":
      case "interface-3": {
        const n = screen.split("-")[1];
        const names = { "1": "Chatbot", "2": "AmbiSQL-inspired", "3": "Context-aware" };
        return (
          <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <BlankSlot label={`Interface ${n} — ${names[n]} (to be built)`} />
          </div>
        );
      }

      case "output-1":
      case "output-2":
      case "output-3": {
        const n = screen.split("-")[1];
        return (
          <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <BlankSlot label={`Output ${n} — database rows + description (to be built)`} />
          </div>
        );
      }

      case "feedback-1":
      case "feedback-2":
      case "feedback-3": {
        const fb = feedback[screen] || {};
        const setFb = (k, v) => setFeedback((f) => ({ ...f, [screen]: { ...f[screen], [k]: v } }));
        return (
          <div style={{ maxWidth: 900, margin: "0 auto", width: "100%", color: BLACK }}>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: "0 0 16px" }}>User feedback</h1>
            <LikertRow prompt="The response gave me what I wanted" value={fb.q1} onChange={(v) => setFb("q1", v)} />
            <LikertRow prompt="The interface was intuitive and easy to use" value={fb.q2} onChange={(v) => setFb("q2", v)} />
            <div style={{ fontSize: 16, marginBottom: 6 }}>Any further thoughts? (optional)</div>
            <textarea
              value={fb.text || ""}
              onChange={(e) => setFb("text", e.target.value)}
              rows={3}
              style={{ width: "100%", padding: 12, fontFamily: FONT, fontSize: 15, border: BORDER, borderRadius: 0, boxSizing: "border-box", resize: "none" }}
            />
          </div>
        );
      }

      case "end":
        return (
          <Centered>
            <p style={{ fontWeight: 700 }}>Thank you — the study is complete.</p>
            <p style={{ fontSize: 18 }}>You may now close this window.</p>
          </Centered>
        );

      default:
        return null;
    }
  }

  if (exited) {
    return (
      <div style={{ fontFamily: FONT, background: GREY, minHeight: 560, display: "flex", alignItems: "center", justifyContent: "center", padding: 40 }}>
        <div style={{ textAlign: "center", fontSize: 22 }}>
          <p style={{ fontWeight: 700 }}>You have exited the study.</p>
          <button
            onClick={() => { setExited(false); setIndex(0); setSubmitted(0); }}
            style={{ marginTop: 16, padding: "10px 20px", fontFamily: FONT, fontSize: 16, border: BORDER, background: WHITE, cursor: "pointer", borderRadius: 0 }}
          >
            Restart (prototype only)
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: FONT, background: GREY, minHeight: 560, height: "100vh", display: "flex", flexDirection: "column", position: "relative", color: BLACK }}>
      {/* content */}
      <div style={{ flex: 1, minHeight: 0, padding: "28px 32px", overflow: "hidden", display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", justifyContent: screen === "welcome" || screen === "end" ? "center" : "flex-start" }}>
          {renderScreen()}
        </div>
      </div>

      {/* bottom bar */}
      <div style={{ display: "grid", gridTemplateColumns: "100px 1fr 100px", alignItems: "center", padding: "14px 24px 20px" }}>
        <div>{showBack && <ArrowButton dir="back" onClick={goBack} />}</div>
        <div style={{ textAlign: "center" }}>
          <button
            onClick={() => setConfirming(true)}
            style={{ background: "none", border: "none", fontFamily: FONT, fontSize: 17, color: BLACK, cursor: "pointer", textDecoration: "underline" }}
          >
            Please click here to exit
          </button>
        </div>
        <div style={{ textAlign: "right" }}>{showForward && <ArrowButton dir="forward" onClick={goForward} />}</div>
      </div>

      {/* exit confirm */}
      {confirming && (
        <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.45)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ background: WHITE, border: BORDER, padding: 28, width: 360, textAlign: "center" }}>
            <p style={{ fontSize: 20, fontWeight: 700, margin: "0 0 20px" }}>Exit the study?</p>
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button onClick={() => { setConfirming(false); setExited(true); }} style={{ padding: "10px 22px", background: TEAL, color: WHITE, border: BORDER, fontFamily: FONT, fontSize: 16, fontWeight: 700, cursor: "pointer", borderRadius: 0 }}>Yes, exit</button>
              <button onClick={() => setConfirming(false)} style={{ padding: "10px 22px", background: WHITE, color: BLACK, border: BORDER, fontFamily: FONT, fontSize: 16, cursor: "pointer", borderRadius: 0 }}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
