import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import StudyShell from "./StudyShell.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <StudyShell />
  </StrictMode>
);
