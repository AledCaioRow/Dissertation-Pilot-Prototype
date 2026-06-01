---
tags: [frontend]
---
# C3 Dynamic Host

Live-mounts the model's generated JSX in a sandbox. **This is where the generated JSX goes.**

**Code:** [`frontend/src/components/C3DynamicHost.jsx`](../../frontend/src/components/C3DynamicHost.jsx)

## How it works (plain English)
1. It receives `{ jsx, fields }` from [[Call 1 Interface Generation]] (in stub mode this is a
   realistic, db-specific interface — see [[Stub Call Layer]]).
2. It transpiles the JSX string with Babel-standalone, then mounts it with a scoped `new Function`,
   injecting `React`, the [[C3 Primitives]], and a `submitResponses` function. The snippet must
   define a component named `Interface`.
3. When the participant submits, `submitResponses(obj)` pairs each value with its manifest label and
   emits the shared responses contract — the same shape C2 produces.
4. **Fallback:** if the JSX fails to compile or throws, an error boundary shows a labelled text-input
   form built from the field manifest and records `compile_success=false` (the trial never aborts).
5. A blank placeholder slot only appears for a genuinely empty payload — not in the normal demo.

**Connected:** [[Dynamic Interface]] (spec) · [[C3 Primitives]] · [[Call 1 Interface Generation]] · [[C2 Static Interface]] · [[Overreliance Probe]] · [[Wizard App]]
