import { createRoot } from "react-dom/client";
import StudyShell from "./StudyShell.jsx";

// Note: StrictMode is intentionally omitted. It double-invokes effects in dev,
// which would fire the side-effectful model calls (C1 chat, C3 dynamic) twice.
createRoot(document.getElementById("root")).render(<StudyShell />);
