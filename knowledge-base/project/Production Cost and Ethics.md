---
tags: [project]
---
# Production Cost and Ethics

What it takes to run this for real, and the safety/ethics posture — for a **local, supervised,
in-person** study (no public hosting).

## Cost (when live)
- Two model calls per trial: call 1 (interface) + call 2 (SQL gen + post-execution explanation).
  C3's call 1 returns JSX, so it is the heavier of the two conditions; C2's is small fixed widgets.
- Four trials per participant (2×C2 + 2×C3). The [[Logging|call log]] records tokens + latency for
  every call, which is exactly the cost side of the C2-vs-C3 comparison.
- SQL execution is local and free; the only paid part is the Anthropic calls.

## Safety
- The Anthropic key lives only in `backend/.env` on the laptop and never reaches the browser.
- **C3 mounts model-generated JSX.** The risk is low here because it's a controlled, supervised,
  in-person session on the researcher's machine — not public — and the JSX runs in a scoped sandbox
  ([[C3 Dynamic Host]]) limited to the whitelisted [[C3 Primitives]], with an error-boundary fallback.
- Databases are opened read-only; the study never writes to them.

## Ethics / data
- Consent + eligibility screening gate entry; a persistent footer offers contact + withdraw at any time.
- Logs are anonymised (`participant_id` only) and stored locally as one JSON file per participant.
- Neutral, non-leading copy throughout (no "AI", no praise) so confidence/overreliance aren't nudged.

**Connected:** [[Local Launch]] · [[Stub vs Live]] · [[Logging]] · [[Overreliance Probe]] · [[C3 Dynamic Host]] · [[Build Brief]]
