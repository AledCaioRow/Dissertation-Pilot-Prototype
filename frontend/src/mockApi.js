// Client-side mock of the session API, so the wizard runs with no backend.
// Mirrors the real contracts. The C3 interface is returned as a BLANK PLACEHOLDER
// ({ jsx: "", placeholder: true }) — the empty slot where the model's generated JSX will
// be live-mounted later. C2 still returns real multiple-choice widgets so both condition
// shells are visible.

const DBS = {
  california_schools: {
    name: "california_schools",
    placeholder: true,
    tables: [
      { name: "schools", columns: [
        { name: "CDSCode", type: "TEXT", pk: true }, { name: "School", type: "TEXT" },
        { name: "District", type: "TEXT" }, { name: "County", type: "TEXT" }, { name: "City", type: "TEXT" }] },
      { name: "satscores", columns: [
        { name: "cds", type: "TEXT", pk: true }, { name: "NumTstTakr", type: "INTEGER" },
        { name: "AvgScrRead", type: "INTEGER" }, { name: "AvgScrMath", type: "INTEGER" },
        { name: "AvgScrWrite", type: "INTEGER" }] },
      { name: "frpm", columns: [
        { name: "CDSCode", type: "TEXT", pk: true }, { name: "Enrollment (K-12)", type: "REAL" },
        { name: "Free Meal Count (K-12)", type: "REAL" }] },
    ],
  },
  financial: {
    name: "financial",
    placeholder: true,
    tables: [
      { name: "district", columns: [{ name: "district_id", type: "INTEGER", pk: true }, { name: "A2", type: "TEXT" }, { name: "A3", type: "TEXT" }] },
      { name: "account", columns: [{ name: "account_id", type: "INTEGER", pk: true }, { name: "district_id", type: "INTEGER" }, { name: "date", type: "DATE" }] },
      { name: "client", columns: [{ name: "client_id", type: "INTEGER", pk: true }, { name: "gender", type: "TEXT" }, { name: "birth_date", type: "DATE" }] },
      { name: "trans", columns: [{ name: "trans_id", type: "INTEGER", pk: true }, { name: "account_id", type: "INTEGER" }, { name: "date", type: "DATE" }, { name: "type", type: "TEXT" }, { name: "amount", type: "INTEGER" }] },
    ],
  },
};

// A fixed, balanced assignment (schema order, C2-then-C3, slot pattern 0).
const ASSIGNMENT = {
  participant_id: 0,
  index: 0,
  n_assignments: 8,
  schema_order: ["california_schools", "financial"],
  condition_block_order: ["C2", "C3"],
  slot_pattern: 0,
  authoring_plan: [
    { database: "california_schools", ambiguity_class: "schema_reference", slot: 0, condition: "C2" },
    { database: "california_schools", ambiguity_class: "superlative_metric", slot: 1, condition: "C3" },
    { database: "financial", ambiguity_class: "value_reference", slot: 0, condition: "C2" },
    { database: "financial", ambiguity_class: "temporal_window", slot: 1, condition: "C3" },
  ],
  slot_to_condition: {
    "california_schools:schema_reference": "C2",
    "california_schools:superlative_metric": "C3",
    "financial:value_reference": "C2",
    "financial:temporal_window": "C3",
  },
};

const conditionByTrial = {}; // trial_id -> "C2" | "C3"

const C2_WIDGETS = {
  widgets: [
    {
      id: "amb_1", ambiguity_type: "unclear_schema_reference",
      title: "Which figure should we use to compare?",
      description: "There are several numbers we could rank or compare by.",
      options: [
        { value: "overall", label: "The overall, combined figure", snippet: "e.g. a total across several score columns" },
        { value: "single", label: "A single specific figure", snippet: "e.g. one score column on its own" },
        { value: "count", label: "How many took part", snippet: "e.g. a count of records" },
      ],
    },
    {
      id: "amb_2", ambiguity_type: "unclear_value_reference",
      title: "How should we match the place or category you mentioned?",
      description: "It could be stored in more than one way.",
      options: [
        { value: "broad", label: "The broader grouping", snippet: "e.g. a county / region column" },
        { value: "narrow", label: "The narrower one", snippet: "e.g. a city / specific column" },
      ],
    },
  ],
  allow_additional_constraints: true,
};

// The C3 manifest — the fields the (not-yet-generated) interface would collect.
const C3_PLACEHOLDER = {
  jsx: "", // intentionally empty: the host renders the blank placeholder slot
  placeholder: true,
  fields: [
    { id: "metric", label: "Which measure should count here?" },
    { id: "threshold", label: "Only include results at or above this level" },
    { id: "matchAll", label: "Must every condition be met? (all vs any)" },
    { id: "note", label: "Anything else to add?" },
  ],
};

const ok = async () => ({ ok: true });

export const mockApi = {
  getConfig: async () => ({ loading_screen_min_seconds: 1, question_authoring_min_chars: 15, show_result_row_limit: 50, stubbed: true, mock: true }),
  startSession: async () => ({ assignment: ASSIGNMENT, describe: "(mock) demo assignment", resumed: false }),
  consent: ok,
  screening: ok,
  getSchema: async (name) => DBS[name] || { name, placeholder: true, tables: [] },
  author: async ({ db_name, ambiguity_class }) => {
    const trial_id = `${db_name}:${ambiguity_class}`;
    const condition = ASSIGNMENT.slot_to_condition[trial_id] || "C2";
    conditionByTrial[trial_id] = condition;
    return { trial_id, condition };
  },
  trialInterface: async (_pid, trial_id) => {
    const condition = conditionByTrial[trial_id] || ASSIGNMENT.slot_to_condition[trial_id] || "C2";
    return { condition, data: condition === "C3" ? C3_PLACEHOLDER : C2_WIDGETS };
  },
  trialAnswer: async () => ({
    interpretation: "(demo) A plain restatement of your request would appear here.",
    sql: "SELECT s.School AS school, x.AvgScrMath + x.AvgScrRead + x.AvgScrWrite AS score\nFROM schools s JOIN satscores x ON x.cds = s.CDSCode\nORDER BY score DESC\nLIMIT 5;  -- demo (mock mode)",
    explanation: "(demo) In mock mode there's no real database, so this is a stand-in result. With the backend running, the system runs the query and explains the actual rows here.",
    rows: [["Example High School", 1530], ["Another High School", 1495], ["A Third School", 1480]],
    column_names: ["school", "score"],
    success: true,
    error: null,
    row_count: 3,
  }),
  perceived: ok,
  questionnaire: ok,
  debrief: ok,
  withdraw: async () => ({ ok: true, withdrawn: true }),
};
