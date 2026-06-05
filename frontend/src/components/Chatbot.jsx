import { useEffect, useRef, useState } from "react";
import { postJSON } from "../lib/api.js";

// C1 — Chatbot. A plain message thread pre-loaded with the person's question.
// One round-trip to /api/chat (the model returns its plain-language understanding
// plus any clarifying questions); the person replies once; then we hand the whole
// transcript to /api/finalize as `clarifications` and move to the output screen.
// Deliberately plain — no suggestion chips or structured controls — so it
// contrasts with C2/C3.

const TEAL = "#156082";
const LIGHT = "#E8E8E8";
const BLACK = "#000000";
const WHITE = "#FFFFFF";
const FONT = "Arial, Helvetica, sans-serif";
const BORDER = `3px solid ${BLACK}`;

export default function Chatbot({ sessionId, questionIndex, question, onResolve, onLog }) {
  const [messages, setMessages] = useState([{ role: "user", content: question }]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(true);
  const [replied, setReplied] = useState(false);
  const [error, setError] = useState(null);
  const scroller = useRef(null);
  const asked = useRef(false);

  // First turn: ask the model for its understanding + clarifying questions.
  useEffect(() => {
    if (asked.current) return;
    asked.current = true;
    (async () => {
      try {
        const out = await postJSON("/api/chat", {
          session_id: sessionId,
          question_index: questionIndex,
          history: [{ role: "user", content: question }],
        });
        onLog?.("chat_receive", { value: { len: out.reply?.length } });
        setMessages((m) => [...m, { role: "assistant", content: out.reply }]);
      } catch (e) {
        setError(String(e.message || e));
      } finally {
        setBusy(false);
      }
    })();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (scroller.current) scroller.current.scrollTop = scroller.current.scrollHeight;
  }, [messages, busy]);

  const sendReply = () => {
    const text = draft.trim();
    if (!text || replied || busy) return;
    onLog?.("chat_send", { value: { len: text.length } });
    setMessages((m) => [...m, { role: "user", content: text }]);
    setDraft("");
    setReplied(true);
  };

  const finish = async () => {
    // Serialise the transcript as the clarifications for the finaliser. The C1
    // window already contains the model's clarification + the person's reply.
    const transcript = messages
      .map((m) => `${m.role === "user" ? "Person" : "Assistant"}: ${m.content}`)
      .join("\n");
    onLog?.("chat_send", { value: { finalize: true } });
    await onResolve(transcript);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 12, color: BLACK }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Chat about your question</h1>

      <div ref={scroller} style={{ flex: "1 1 auto", minHeight: 0, overflowY: "auto", border: BORDER, background: WHITE, padding: 14, display: "flex", flexDirection: "column", gap: 10 }}>
        {messages.map((m, i) => (
          <Bubble key={i} role={m.role}>{m.content}</Bubble>
        ))}
        {busy && <Bubble role="assistant"><i>…thinking…</i></Bubble>}
        {error && <div style={{ color: "#7a1f1f", fontSize: 14 }}>Error: {error}</div>}
      </div>

      {!replied ? (
        <div style={{ display: "flex", gap: 10 }}>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") sendReply(); }}
            disabled={busy || !!error}
            placeholder="Reply to the assistant…"
            style={{ flex: 1, padding: "12px 14px", fontFamily: FONT, fontSize: 16, border: BORDER, borderRadius: 0, boxSizing: "border-box" }}
          />
          <button onClick={sendReply} disabled={busy || !draft.trim() || !!error} style={btn(!busy && !!draft.trim())}>
            Send
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button onClick={finish} style={btn(true)}>Get my answer →</button>
        </div>
      )}
    </div>
  );
}

function Bubble({ role, children }) {
  const isUser = role === "user";
  return (
    <div style={{ alignSelf: isUser ? "flex-end" : "flex-start", maxWidth: "78%" }}>
      <div style={{ fontSize: 11, color: "#5f6b70", marginBottom: 2 }}>{isUser ? "You" : "Assistant"}</div>
      <div style={{ background: isUser ? TEAL : LIGHT, color: isUser ? WHITE : BLACK, border: BORDER, padding: "10px 12px", fontSize: 15, lineHeight: 1.4, whiteSpace: "pre-wrap" }}>
        {children}
      </div>
    </div>
  );
}

function btn(enabled) {
  return { padding: "0 24px", background: enabled ? TEAL : "#9bb6c1", color: WHITE, border: BORDER, fontFamily: FONT, fontSize: 16, fontWeight: 700, cursor: enabled ? "pointer" : "default", borderRadius: 0 };
}
