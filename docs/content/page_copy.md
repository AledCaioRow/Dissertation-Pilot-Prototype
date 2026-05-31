# Spoke: page copy

Canonical spec and initial content for everything the participant reads. Becomes `frontend/src/content/copy.json`, loaded by the frontend so wording is a one-file edit with no code change. British English throughout. Deliberately bland and jargon-free — participants know nothing about SQL, databases, or schemas.

The wizard is a step-through: one idea per screen, a visible **Back** button on every screen except where noted (consent, loading, and submitted questionnaires are not reversible).

`{...}` marks copy that depends on the live schema or on your ethics wording — fill before use. The six authoring prompts are drafts grounded in each schema's likely contents; **verify the role-play framings make sense once you've seen the real columns.**

---

## Phase 1 — Consent & details (no Back)

**Heading:** Before we start
**Body:** Thank you for taking part. This study looks at how people ask questions of a computer system to get information out of a database. You do not need to know anything about databases or computing. The session takes about {75–90} minutes.
**Consent block (checkboxes, all required):**
- I confirm I have read and understood the information sheet. {link/handout}
- I understand my participation is voluntary and I may stop at any time, including asking for my session recording to be deleted, without giving a reason.
- I understand the session {will be audio-recorded} and that my data will be stored securely and anonymised.
- I agree to take part.
**Fields:** Name {for consent records only}; contact email {for withdrawal requests}; participant ID {auto-filled}.
**Button:** Begin

> Ethics note (not shown to participant): full consent wording and the information sheet come from your Wrexham ethics application. The fields above are the minimum; the data-use explanation lives on the next screen.

---

## Phase 2 — Study explanation (Back enabled)

**Heading:** What you'll be doing
**Body:** You'll look at two different collections of information — think of each like a set of linked tables, the sort of thing an organisation keeps its records in. For each one, we'll ask you to come up with a couple of questions you'd genuinely want answered, in your own words. A computer system will then try to help you turn each question into a precise request and show you an answer. After each set, we'll ask what you thought. There are no right or wrong questions, and nothing here is a test of you — we're testing the system. You'll do this on your own, at your own pace.
**Persistent footer (every screen from here):** Questions? Contact {researcher name / email}.  ·  [Exit and withdraw]
**Button:** Next

---

## Phase 3 — Authoring, per database (×2, Back enabled)

Each database gets an intro screen then two authoring screens (one per hosted question). The participant never sees the words "ambiguity" or the class names.

### 3a. Database intro (per schema)

**california_schools**
> **Heading:** The schools records
> **Body:** This collection is about schools in California — each school's details, its exam (SAT) results, and figures on how many pupils qualify for free or reduced-price meals. Imagine you work in a **schools district office** and someone's asked you to pull together some figures.
> **Button:** Next

**financial**
> **Heading:** The bank records
> **Body:** This collection is about a bank — its customers, their accounts, the cards and loans on those accounts, and the transactions that go through them. Imagine you're an **analyst at the bank** answering a question from a manager.
> **Button:** Next

### 3b. Authoring screens — the six prompts

Each screen shows the role framing, the task, the schema (bland), a **question box**, an **intent-note box**, and Back. Each prompt steers toward a deliberately complex query (a join plus one more demanding operation) while leaving the substance to the participant. The bracketed class is for *your* records only and is **not shown**.

**california_schools / [schema_reference]**
> Working in the district office, write a question that compares schools using **how well their pupils did** — but you decide what "did well" should mean here. Make it a question that needs you to bring schools and their results together.
> *Then:* which schools are you expecting to come back, and why?

**california_schools / [superlative_metric]**
> Write a question asking for the **top school (or top few schools)** by some measure of your choosing, in a particular area of California.
> *Then:* what exactly would count as "the top" for you, and how many schools did you expect?

**financial / [value_reference]**
> As the bank analyst, write a question about a **particular kind of transaction or a particular place** (a district), and which customers or accounts it involves.
> *Then:* describe in plain words what you're trying to find.

**financial / [temporal_window]**
> As the bank analyst, write a question about activity over **some period of time** that you describe in your own words (for example "recently", "last year", "over the summer"), involving accounts and their transactions.
> *Then:* what period did you have in mind, and what answer are you expecting?

**Soft validation:** if the question box has fewer than `QUESTION_AUTHORING_MIN_CHARS` characters, show a gentle nudge ("Could you write a little more?") — do not block.

---

## Phase 4 / 6 — Loading screen (no Back)

**Heading:** One moment
**Body:** The system is preparing a few questions to make sure it understands exactly what you mean…
(Shows for at least `LOADING_SCREEN_MIN_SECONDS` so it appears even when C2 is fast, keeping C2 and C3 comparable.)

---

## Phase 4 / 6 — Interface screens

The interface itself is rendered by `C2StaticInterface` or `C3DynamicHost`. Surrounding copy:

**Standing instruction (above the interface):** Answer these to help the system understand exactly what you mean.
**Submit button label:** Show me the answer

### Interface-confidence (shown *before* results render)

**Question (single screen, after submit, before output):**
> Before you see the answer — do you feel this captured what you were asking for?
> ◯ Yes, completely  ◯ Mostly  ◯ Partly  ◯ Not really  ◯ No

---

## Phase 4 / 6 — Output + explanation

**Heading:** Here's the answer
**Body (above the table):** Based on what you told the system, here's what it found.
(`ResultView` shows: the **result table**, then the **plain-language explanation**, then the **exact query the system wrote** under a heading like "The request the system built for you" — shown verbatim even though the participant may not read it. On an execution error, instead show: "The system couldn't work out an answer to this one. That's useful for us to know — let's carry on.")

### Answer-confidence (shown *after* results render)

> Is this the answer you wanted?  ◯ Yes  ◯ No
> How confident are you that this answer is correct?
> ◯ Not at all  ◯ Slightly  ◯ Moderately  ◯ Very  ◯ Completely

---

## Phase 5 / 7 — Per-condition questionnaire

### System Usability Scale (canonical Brooke 1996 wording — do not paraphrase)

5-point Strongly disagree → Strongly agree.
1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

> Scoring (computed, not shown): odd items score (response − 1); even items score (5 − response); sum × 2.5 → 0–100.

### Agency & clarity items (study-specific)

5-point Strongly disagree → Strongly agree.
1. I felt I contributed to the answer the system gave.
2. The choices the system asked me to make made sense.
3. The interface was simple to use.
4. The interface was confusing.  *(reverse of 3; consistency check)*

### Open-ended (per condition)

- What, if anything, was confusing about this way of asking?
- Was there a point where you weren't sure what the system was asking you?
- Anything you'd change about it?

---

## Phase 8 — Debrief (no Back once submitted)

**Heading:** Last few questions
- Which of the two ways of asking did you prefer overall? ◯ The first  ◯ The second  ◯ No preference
- Why?
- Was there ever a moment where you weren't sure whether the system had actually given you what you asked for? Tell us about it.
- Anything else you'd like to flag?
**Button:** Finish
**Final screen:** Thanks — that's everything. {closing line / any debrief info from ethics}

---

## Notes for the build

- All of the above lives in `copy.json` as keyed strings/arrays; components read keys, never hard-code text.
- The two confidence screens (interface-confidence pre-result, answer-confidence post-result) are separate steps in the wizard, both logged under the trial's `perceived_success`.
- The persistent footer (contact line + Exit-and-withdraw) appears on every screen from the study-explanation page onward. "Exit and withdraw" marks the session log withdrawn and stops further screens.
- Authoring prompts are keyed by `(schema, class)` so they line up with `SCHEMA_CLASS_MAP`; the participant sees only the prose, never the class label.
