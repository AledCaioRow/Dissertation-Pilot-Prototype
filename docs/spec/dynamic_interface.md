# Spoke: C3 — the dynamic (bespoke) interface

Governs the **C3** condition: an interface the model generates per question. This file is the **single source of truth** for the component primitive set — both the host's injected scope (`C3DynamicHost.jsx`) and the C3 generation prompt (`model_prompts.md`) must reference this list so they never drift.

The experimental contrast with C2 lives here: where C2 can only ever offer multiple-choice, C3 may choose a control **matched to the shape of the ambiguity** — a slider for a threshold, a date-range for a temporal window, a toggle for set logic. That affordance freedom is the thing under test.

---

## 1. Call-1 output contract (C3)

Call 1 (C3) returns **only** this JSON object:

```json
{
  "jsx": "<a self-contained React component, using only the injected primitives, that calls submitResponses({...}) on submit>",
  "fields": [
    {"id": "f1", "label": "Which clubs are you asking about?"},
    {"id": "f2", "label": "Do you want members in ALL of them, or ANY of them?"}
  ]
}
```

- `jsx` is the rendered interface. It must use only the primitives in §3 and must call `submitResponses({field_id: value, ...})` once, on its own submit control.
- `fields` is the manifest: every input the component collects, with a plain-language `label`. The host joins the submitted object to this manifest to produce the shared responses contract (§2). Without the manifest, the labels are lost — so a field present in `jsx` but missing from `fields` is a validation error.

pydantic (`io.py`):

```python
class C3Field(BaseModel):
    id: str
    label: str

class BespokeInterface(BaseModel):   # the C3 call-1 output
    jsx: str
    fields: list[C3Field]
```

---

## 2. Shared responses contract (used by BOTH C2 and C3)

When the participant submits, either interface produces the same shape sent to `POST /trial/answer`:

```json
{ "trial_id": "...",
  "responses": [ {"field_id": "f1", "label": "Which clubs are you asking about?", "value": ["chess","debate"]}, ... ] }
```

The host builds this by pairing each key of the `submitResponses({...})` object with its `label` from the manifest. `value` may be a string, number, boolean, array, or `{start, end}` object depending on the control.

---

## 3. The component primitive set (THE single source of truth)

C3-generated JSX may use **only** these, all injected into the sandbox scope. The C3 prompt lists exactly these and nothing else.

| Primitive | Use | `value` shape |
|---|---|---|
| `Radio` | choose one of N | string |
| `Checkboxes` | choose any of N | array of strings |
| `Dropdown` | choose one of N (long lists) | string |
| `MultiSelect` | choose several (long lists) | array of strings |
| `NumberInput` | an exact number | number |
| `Slider` | a number in a range (e.g. a threshold/percentage) | number |
| `DatePicker` | a single date | ISO date string |
| `DateRange` | a date window (start + end) | `{start, end}` ISO strings |
| `Toggle` | a binary choice (e.g. ALL vs ANY) | boolean |
| `ColumnPicker` | point at a column in the shown schema | string (qualified column, e.g. `member.first_name`) |
| `TextInput` | free text (use sparingly) | string |
| `InfoPanel` | display-only explanation; no value | — |

Each control accepts `id`, `label`, and a short plain-language `help` string; range controls accept `min`/`max`/`step`; option controls accept an `options` array of `{value, label, help?}`.

Keep this table and the injected scope identical. If a primitive is added or removed, change it here, in the host, and in the C3 prompt together.

---

## 4. The host (`frontend/src/components/C3DynamicHost.jsx`)

- Receives `{ jsx, fields }` from call 1.
- Renders `jsx` inside a **sandbox** (`react-live`, or Babel-standalone transpile + a scoped `new Function` mount). Inject the scope: `React`, the §3 primitives, and a `submitResponses(obj)` function.
- On `submitResponses(obj)`, pair each key with its manifest `label` → emit the §2 responses contract to `POST /trial/answer`.
- **Fallback:** if `jsx` fails to compile or throws on render, catch it, set `compile_success = false` on the call-log record, and render a generic component listing each manifest `field` as a labelled `TextInput`. The trial proceeds; never abort on a compile failure.

---

## 5. Generation rules (enforced by the C3 prompt — see `model_prompts.md`)

The model must:
- Identify whatever ambiguities or missing information most affect correct SQL for *this* question against *this* schema — not limited to any taxonomy.
- Compose a small interface (cap ~6 inputs), choosing for each ambiguity the primitive whose **shape fits** (threshold → `Slider`/`NumberInput`; date window → `DateRange`; set logic → `Toggle` or `Radio`; which-column → `ColumnPicker` or `Radio`; which-values → `Checkboxes`/`MultiSelect`).
- Order inputs most- to least-consequential.
- Write every `label`/`help` in plain domain language a non-expert can answer — **never** SQL terms (no "INNER vs LEFT JOIN", no column types).
- Emit exactly the §1 object, with a `fields` manifest covering every input, and a component that calls `submitResponses(...)` once.

---

## 6. What to log

Per C3 trial: the raw `jsx` (so you can see what was generated), the `fields` manifest, `compile_success`, the participant's submitted values, and (from the call log) the interface-generation token count and latency — the inputs to the C2-vs-C3 cost comparison.

---

## Related (knowledge base)
- [[C3 Dynamic Host]] (host) · [[C3 Primitives]] (the primitive set) · [[Call 1 Interface Generation]]
- [[The Experiment C2 vs C3]] · [[ambisql_static_interface]] (the C2 contrast) · [[Home]]
