---
tags: [frontend]
---
# C3 Dynamic Host

Live-mounts the model's generated JSX in a sandbox. **This is where the generated JSX goes.**

**Code:** [`frontend/src/components/C3DynamicHost.jsx`](../frontend/src/components/C3DynamicHost.jsx)

**Key points**
- Babel-standalone transpiles `jsx`; a scoped `new Function` mounts it, injecting `React`, the
  [[C3 Primitives]], and `submitResponses`. The snippet must define a component named `Interface`.
- **Blank placeholder:** when the payload is empty/`placeholder` (e.g. mock mode), it renders a
  dashed slot — *"the generated interface will mount here"* — with the field manifest and a
  proceed button. See [[API Client and Mock]].
- **Fallback:** compile/runtime error → a labelled text-input form, `compile_success=false`
  (never aborts the trial).
- `submitResponses(obj)` pairs keys with the manifest labels → shared responses contract.

**Connected**
- [[dynamic_interface]] (spec, §4 host) · [[Call 1 Interface Generation]] · [[C2 Static Interface]]
- [[Overreliance Probe]] · [[Wizard App]]
