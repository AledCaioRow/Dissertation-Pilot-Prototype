"""Generates methods.docx in the project root."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Styles ──────────────────────────────────────────────────────────────────

def set_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.color.rgb = RGBColor(0x1a, 0x1a, 0x2e)
    return p

def body(doc, text):
    p = doc.add_paragraph(text)
    p.style.font.size = Pt(11)
    return p

def code_block(doc, text, caption=None):
    """Add a shaded code block paragraph."""
    if caption:
        c = doc.add_paragraph(caption)
        c.runs[0].font.size = Pt(9)
        c.runs[0].font.italic = True
        c.runs[0].font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(9)

    # Light grey shading on the paragraph
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F2F2")
    pPr.append(shd)

    # Indent
    pPr2 = para._p.get_or_add_pPr()
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "360")
    ind.set(qn("w:right"), "360")
    pPr2.append(ind)
    return para

def bullet(doc, text, level=0):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.left_indent = Inches(level * 0.25)
    return p

def label(doc, text):
    """Bold inline label for table-like descriptions."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    return p

# ── Title ────────────────────────────────────────────────────────────────────

doc.add_heading("Study Methods", 0)
doc.add_paragraph(
    "This document describes the design and methods of a controlled study comparing "
    "three AI-powered interfaces for helping people ask questions of a database in plain English."
)

# ── 1. Research Question ─────────────────────────────────────────────────────

set_heading(doc, "1. What the Study is Testing", 1)

body(doc,
    "When a person asks a database a question in plain English, their question is "
    "often ambiguous — it could mean more than one thing. The AI needs to clarify "
    "what they mean before it can write the right database query."
)
body(doc,
    "This study asks: does the design of that clarification step affect how well "
    "people get what they want? Three designs are tested. Everything else — the AI model, "
    "the database, the prompts, the temperature — is held constant. Only the interface changes."
)

# ── 2. The Database ───────────────────────────────────────────────────────────

set_heading(doc, "2. The Database Participants Query", 1)

body(doc,
    "Participants query the student_club database — a realistic snapshot of a university "
    "club's 2019–20 academic year. It was chosen from an established SQL benchmark "
    "(the Spider dataset) because it is complex enough to produce genuinely ambiguous "
    "questions, but familiar enough that participants do not need any specialist knowledge "
    "to understand it."
)
body(doc, "The database contains five main areas:")
for row in [
    ("Members", "name, email, position (Member/President/Treasurer), major, T-shirt size"),
    ("Events", "name, date, type (Meeting/Game/Social/Election/etc.), location, status"),
    ("Budget", "per-event budget lines, broken down by category (Food, Advertising, etc.)"),
    ("Expenses & Income", "individual costs paid and money received, linked to events"),
    ("Attendance", "which members attended which events"),
]:
    bullet(doc, f"{row[0]}: {row[1]}")

body(doc,
    "The database is opened read-only at the connection level. The AI is never given "
    "a live query tool — it can only see a frozen description of the schema and sample data. "
    "This prevents it from exploring the database on its own."
)
code_block(doc,
    '# content_db.py  line 37\n'
    'uri = f"file:{DB_PATH}?mode=ro"\n'
    'conn = sqlite3.connect(uri, uri=True)\n'
    'conn.execute("PRAGMA query_only = ON;")',
    caption="backend/content_db.py — the database connection is read-only at both the URI and driver level"
)

# ── 3. The Three Conditions ───────────────────────────────────────────────────

set_heading(doc, "3. The Three Conditions", 1)

body(doc,
    "Each participant works through all three conditions, one per question they wrote. "
    "The order can be counterbalanced. The conditions differ only in what happens during "
    "the clarification step — the first turn in the conversation."
)

# C1
set_heading(doc, "Condition 1 — Chatbot (plain text)", 2)
body(doc,
    "The AI reads the participant's question and replies in plain English, explaining "
    "what it understood and asking about anything still unclear. The participant types "
    "a reply. This is the simplest design — no structure, no controls, just text."
)
body(doc, "The system prompt that drives this condition (A1_CHATBOT):")
code_block(doc,
    "YOUR TASK\n"
    "Find the parts of the person's question that are unclear or could be read more than\n"
    "one way and that would change the SQL query needed to answer it. Then reply in one\n"
    "short, plain-language message telling them what you understood and asking about\n"
    "anything still unclear.\n\n"
    "OUTPUT\n"
    "One plain-language message, with no technical or database terms. You do not write\n"
    "SQL here; after the person's single reply you will be asked for the query.",
    caption="backend/prompts.py — A1_CHATBOT system prompt (abridged; the full context block precedes this)"
)

# C2
set_heading(doc, "Condition 2 — Wizard (structured, fixed UI)", 2)
body(doc,
    "The AI reads the question and returns structured JSON listing every ambiguity it found, "
    "along with a UI control type for each one. A fixed wizard interface on screen then renders "
    "those controls — one at a time — so the participant can resolve them without typing. "
    "This design is inspired by the AmbiSQL framework from prior NLP research."
)
body(doc, "The AI is instructed to return JSON in exactly this shape:")
code_block(doc,
    '{\n'
    '  "originalQuestion": "<unchanged>",\n'
    '  "summary": "<plain-English restatement>",\n'
    '  "ambiguities": [\n'
    '    {\n'
    '      "id": "snake_case_id",\n'
    '      "phrase": "<exact words from question>",\n'
    '      "type": "ambiguous_temporal_spatial_scope",\n'
    '      "affordance": "dateRange",   // choice | value | range | toggle | dateRange\n'
    '      "clarificationQuestion": "Which date range should be included?",\n'
    '      "evidence": "event.event_date",\n'
    '      "dateRange": { "earliest": "2019-08-01", "latest": "2020-05-31" }\n'
    '    }\n'
    '  ]\n'
    '}',
    caption="backend/prompts.py — example of the JSON structure the A2_AMBIGUITY prompt demands"
)
body(doc,
    "The 'affordance' field tells the frontend which control to render: a radio button group, "
    "a dropdown, a slider, a yes/no toggle, or a date range picker. The values in those "
    "controls come only from the frozen database description — the AI cannot invent options "
    "that don't exist in the data."
)

# C3
set_heading(doc, "Condition 3 — Dynamic (AI-generated interface)", 2)
body(doc,
    "The AI generates a custom React component tailored to the participant's specific question. "
    "The interface is rendered in a sandboxed iframe — it cannot access the internet or the "
    "parent page. The ambiguity list used to generate the component is the same list that "
    "Condition 2 would use, so the AI's reading of what is ambiguous is held constant between "
    "the two conditions. Only the interface design changes."
)
code_block(doc,
    "OUTPUT (strict)\n"
    "Return CODE ONLY — no prose, no markdown fences, no imports. Write one React function\n"
    "component named Clarifier that uses ONLY these injected globals:\n"
    "- React (use hooks as React.useState, etc.)\n"
    "- onResolve(resolutions): call ONCE when the person finishes.\n"
    "- logEvent(type, payload): call on EVERY interaction.\n"
    "Constraints:\n"
    "- No import/require, no fetch/network, no access to window or document.\n"
    "- Begin your output with: function Clarifier() {",
    caption="backend/prompts.py — A3_DYNAMIC system prompt (the instruction to produce React code)"
)
body(doc,
    "The component is sandboxed with a Content Security Policy of connect-src 'none', "
    "meaning it cannot make any network requests. React, ReactDOM, and Babel are bundled "
    "locally — no external CDN calls."
)

# ── 4. What Stays the Same ────────────────────────────────────────────────────

set_heading(doc, "4. What Stays the Same Across All Three Conditions", 1)

body(doc,
    "The study is designed so that only the interface varies. Everything that could "
    "otherwise explain differences in results is held constant:"
)

# Temperature
set_heading(doc, "Temperature = 0 (no randomness)", 2)
body(doc,
    "Every model call is made at temperature 0. This means the model gives the same "
    "output for the same input every time — randomness cannot become a confound. "
    "If two participants wrote identical questions, they would receive identical AI responses."
)
code_block(doc,
    "# backend/llm.py  lines 37-43\n"
    'request_json = {\n'
    '    "model": MODEL,\n'
    '    "max_tokens": MAX_TOKENS,\n'
    '    "temperature": 0,     # enforced here, not in the prompt\n'
    '    "system": system,\n'
    '    "messages": messages,\n'
    '}',
    caption="backend/llm.py — temperature is set once here, never overridable by a prompt"
)

# DB context
set_heading(doc, "The frozen database description", 2)
body(doc,
    "The AI's knowledge of the database comes from a file called DB_CONTEXT.md — a fixed "
    "snapshot of the schema, foreign keys, and sample data. This file is read once at "
    "startup and injected verbatim into every model call for every condition. "
    "No condition is given more or better database information than another."
)
code_block(doc,
    "# backend/prompts.py  lines 17-33\n"
    'DB_CONTEXT = (_HERE / "DB_CONTEXT.md").read_text(encoding="utf-8")\n\n'
    '# Injected into every condition\'s system prompt:\n'
    'DATABASE = (\n'
    '    "DATABASE: student_club (SQLite). The following is the only thing "\n'
    '    "you know about it:\\n\\n"\n'
    '    f"{DB_CONTEXT}"\n'
    ')',
    caption="backend/prompts.py — DB_CONTEXT is read once and never regenerated per call"
)

# Same model
set_heading(doc, "Same AI model for all conditions", 2)
body(doc,
    "A single model name is set via an environment variable (defaulting to claude-sonnet-4-6). "
    "The same model is used for every condition's calls — ambiguity detection, interface "
    "generation, and finalisation."
)
code_block(doc,
    "# backend/llm.py  line 12\n"
    'MODEL = os.getenv("STUDY_MODEL", "claude-sonnet-4-6")',
    caption="backend/llm.py — one model, set once"
)

# Finaliser
set_heading(doc, "The finaliser prompt (identical for all three conditions)", 2)
body(doc,
    "After the participant resolves their ambiguities — however they did it — the backend "
    "appends a second turn to the same conversation. This second turn is word-for-word "
    "identical for C1, C2, and C3. It tells the AI to write the SQL query and a short "
    "explanation in a strict format."
)
code_block(doc,
    "EXPLANATION: <one plain-English paragraph, 50 words or fewer>\n"
    "CONFIDENCE: <a single integer 0-100>\n"
    "SQL:\n"
    "<one or more SQLite SELECT statements — last thing in the response>\n\n"
    "SQL rules:\n"
    "- SELECT statements only. No INSERT/UPDATE/DELETE/CREATE/PRAGMA.\n"
    "- Prefer a single statement. Use more than one ONLY when the question\n"
    "  genuinely cannot be answered by one query.\n"
    "- Use only tables and columns from the schema.",
    caption="backend/prompts.py — OUTPUT_CONTRACT, the shared format all three conditions must produce"
)
body(doc,
    "The finaliser's SQL is then validated (SELECT-only, no comments, no forbidden keywords) "
    "and run against the read-only database. Up to 15 preview rows are shown to the participant; "
    "the full result is stored for analysis."
)

# ── 5. Two-Turn Design ────────────────────────────────────────────────────────

set_heading(doc, "5. The Two-Turn Design", 1)

body(doc,
    "Each question goes through exactly two AI turns. The turns share a conversation "
    "window — the model sees both when producing the final answer."
)
code_block(doc,
    "Turn 1  (differs by condition)\n"
    "  C1 → plain text clarification question     [A1_CHATBOT system prompt]\n"
    "  C2 → JSON ambiguity spec                   [A2_AMBIGUITY system prompt]\n"
    "  C3 → React component source code           [A3_DYNAMIC system prompt]\n\n"
    "             ↓  participant resolves ambiguities  ↓\n\n"
    "Turn 2  (IDENTICAL for C1, C2, C3)\n"
    "  Finaliser appends participant's answers → model writes SQL\n"
    "  Output: EXPLANATION + CONFIDENCE + SQL",
    caption="The two-turn model — the first turn varies, the second is always the same"
)
body(doc,
    "This design means the finaliser 'sees what it built' in Turn 1 — the context is "
    "continuous. It also means any difference in SQL quality between conditions cannot "
    "be blamed on the finaliser prompt, because that prompt never changes."
)

# ── 6. Participant Flow ───────────────────────────────────────────────────────

set_heading(doc, "6. Participant Flow", 1)

code_block(doc,
    "Welcome\n"
    "  ↓\n"
    "Consent  (4 checkboxes: recording, anonymisation, voluntary, data use)\n"
    "  ↓\n"
    "Demographics  (age band, SQL experience, database/spreadsheet frequency)\n"
    "  ↓\n"
    "Guidance  (how to write a good, ambiguous question)\n"
    "  ↓\n"
    "Task  (write 3 plain-English questions about the student club)\n"
    "  ↓\n"
    "┌─────────────────────────────────────────────┐\n"
    "│  For each of the 3 questions (× 3 conditions)│\n"
    "│                                             │\n"
    "│  Interface  →  Resolve ambiguities          │\n"
    "│  Output     →  See the AI's SQL result      │\n"
    "│  Feedback   →  2 Likert-5 ratings           │\n"
    "└─────────────────────────────────────────────┘\n"
    "  ↓\n"
    "End",
    caption="frontend/src/StudyShell.jsx — the full participant journey"
)
body(doc,
    "Participants write their own questions because ecological validity matters — "
    "they know what they want to know. Pre-written questions would impose the researcher's "
    "idea of what is ambiguous, rather than observing ambiguity as it naturally arises. "
    "The guidance screen asks them to write questions that are ambiguous or multifaceted, "
    "to ensure the clarification step is genuinely needed."
)
body(doc,
    "The condition order is randomisable (counterbalanceable) via a single setting in "
    "the backend. During development it defaults to C1 → C2 → C3."
)
code_block(doc,
    "# backend/main.py  line 33\n"
    'DEFAULT_CONDITION_ORDER = ["1", "2", "3"]  # counterbalance for the real study',
    caption="backend/main.py — condition order"
)

# ── 7. Feedback ───────────────────────────────────────────────────────────────

set_heading(doc, "7. Feedback Collected After Each Condition", 1)

body(doc,
    "After each condition's output is shown, participants answer two Likert-5 questions "
    "about their experience of that interface. These capture subjective user experience — "
    "whether they felt they got what they wanted, and whether the interface was easy to use."
)
body(doc, "The two questions are:")
bullet(doc, '"The response gave me what I wanted"  (1 = strongly disagree, 5 = strongly agree)')
bullet(doc, '"The interface was intuitive and easy to use"  (1 = strongly disagree, 5 = strongly agree)')
body(doc, "Participants can also leave optional free-text comments after each condition.")

# ── 8. What is Logged ─────────────────────────────────────────────────────────

set_heading(doc, "8. What is Logged", 1)

body(doc,
    "Every interaction and model call is written synchronously to two places: "
    "a SQLite database (study_logs.sqlite) and an append-only backup file (events.jsonl). "
    "Writes fail loudly — if something cannot be saved, the server returns an error "
    "rather than silently dropping the data."
)
body(doc, "The main tables:")

rows_table = [
    ("sessions", "One row per participant — demographics, condition order, user agent"),
    ("questions", "The full text of each question the participant wrote"),
    ("model_calls", "Every AI call: full request JSON, full response JSON, latency, token counts"),
    ("responses", "The finalised SQL, explanation, confidence score, and full result rows"),
    ("resolution_logs", "What the participant chose in each ambiguity card"),
    ("dynamic_ui", "The generated React component source, whether it rendered or fell back"),
    ("feedback", "The two Likert scores and free text, per condition per question"),
    ("events", "Fine-grained interaction events: every click, selection, screen entry/exit"),
]

table = doc.add_table(rows=1 + len(rows_table), cols=2)
table.style = "Table Grid"
hdr = table.rows[0].cells
hdr[0].text = "Table"
hdr[1].text = "What it stores"
for hcell in hdr:
    for run in hcell.paragraphs[0].runs:
        run.bold = True

for i, (tbl, desc) in enumerate(rows_table):
    row = table.rows[i + 1].cells
    row[0].text = tbl
    row[1].text = desc

doc.add_paragraph()  # spacing after table

# ── Save ──────────────────────────────────────────────────────────────────────

out_path = "/home/user/My-first-Streamlit-app/methods.docx"
doc.save(out_path)
print(f"Saved: {out_path}")
