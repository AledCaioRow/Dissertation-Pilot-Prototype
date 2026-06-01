---
tags: [frontend]
---
# C3 Primitives

The whitelisted UI building blocks the model may use in its generated C3 interface — the fixed
vocabulary that makes the dynamic interface bounded and safe to mount.

**Code:** [`frontend/src/components/c3primitives.jsx`](../../frontend/src/components/c3primitives.jsx)

## How it works (plain English)
1. It exports a fixed set of styled inputs: `Radio`, `Checkboxes`, `Dropdown`, `Slider`,
   `NumberInput`, `TextInput`, `Toggle`, `DateRange`, `ColumnPicker`, plus an `InfoPanel`.
2. Each is a controlled component (`value` + `onChange`) with a consistent label/help layout, so any
   combination the model emits looks coherent.
3. The exact same list is injected into the [[C3 Dynamic Host]] sandbox **and** named in the C3
   prompt, so the model can only use components that actually exist.
4. `ColumnPicker` is fed the database's `table.column` list from [[Schema and Schema Card]].

**Connected:** [[Dynamic Interface]] (spec) · [[C3 Dynamic Host]] · [[Call 1 Interface Generation]] · [[Model Prompts]]
