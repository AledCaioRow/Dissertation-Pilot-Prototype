---
tags: [frontend]
---
# C3 Primitives

The component primitive set — the **only** controls C3-generated JSX may use. Single source of
truth in [[dynamic_interface]] §3, mirrored here and in the C3 prompt's `{primitives}` block.

**Code:** [`frontend/src/components/c3primitives.jsx`](../frontend/src/components/c3primitives.jsx)

**Key points**
- Radio, Checkboxes, Dropdown, MultiSelect, NumberInput, Slider, DatePicker, DateRange, Toggle,
  ColumnPicker, TextInput, InfoPanel — all controlled (`value` + `onChange`).
- `PRIMITIVES` / `PRIMITIVE_NAMES` are injected (in fixed order) into the sandbox by
  [[C3 Dynamic Host]]; `SchemaColumnsContext` feeds ColumnPicker from [[Schema and Schema Card]].
- Add/remove a primitive → change it here, in the host scope, and in the prompt together.

**Connected**
- [[dynamic_interface]] · [[Call 1 Interface Generation]] (prompt `{primitives}`) · [[C3 Dynamic Host]]
