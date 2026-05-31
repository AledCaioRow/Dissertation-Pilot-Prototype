// Phase 4/6 — fixed loading screen (no Back). Runs `task` and holds for at least
// `minSeconds` so it always shows, masking C3's longer call-1 latency (keeps C2/C3 comparable).
import React from "react";
import copy from "../content/copy.json";

export default function LoadingScreen({ task, minSeconds = 2, onDone }) {
  const started = React.useRef(false);
  React.useEffect(() => {
    if (started.current) return; // run once (also guards React StrictMode double-invoke)
    started.current = true;
    const start = Date.now();
    (async () => {
      let result;
      try {
        result = await task();
      } catch (e) {
        result = { error: String(e) };
      }
      const wait = Math.max(0, minSeconds * 1000 - (Date.now() - start));
      if (wait > 0) await new Promise((r) => setTimeout(r, wait));
      onDone(result);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="screen center">
      <h1>{copy.loading.heading}</h1>
      <p>{copy.loading.body}</p>
      <div className="loading-dots">• • •</div>
    </div>
  );
}
