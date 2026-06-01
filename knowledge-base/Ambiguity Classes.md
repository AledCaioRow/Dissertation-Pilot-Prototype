---
tags: [concept]
---
# Ambiguity Classes

The study exercises **four** ambiguity classes across two databases, all inside AmbiSQL's
taxonomy so C2 can genuinely detect every one (the contrast is purely interface affordance):

- `schema_reference` — which table/column to use (california_schools)
- `superlative_metric` — a form of schema-reference: "top by what?" (california_schools)
- `value_reference` — a value that may not match what's stored (financial)
- `temporal_window` — an under-specified time window (financial)

**Key points**
- Mapping lives in `SCHEMA_CLASS_MAP` — see [[Config]].
- The participant never sees these labels; the authoring prompts surface them naturally —
  see [[Copy]] and [[page_copy]].
- The full seven-subcategory taxonomy is in [[ambisql_static_interface]] §3.

**Connected**
- [[Counterbalancing]] — keys assignments by (database, class)
- [[The Experiment C2 vs C3]] · [[Analysis Notebook]] (per-class success)
