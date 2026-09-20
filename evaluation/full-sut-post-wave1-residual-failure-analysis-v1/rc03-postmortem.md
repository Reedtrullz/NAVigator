# RC-03 Postmortem: Structured Routing

## Split

RC-03 is evaluated in two independent parts: structural route representation (RC-03A) and semantic route correctness (RC-03B).

## RC-03A - Structural routing

| Measure | Old baseline | Wave 1 |
|---|---|---|
| Route criteria PASS | 0/108 | 0/108 |
| Structured route emitted (any content) | (old analysis) | 20/108 |
| Empty routes array | - | 88/108 |
| Junk-only routes (headers, revisions, section marks) | - | 8/108 |
| Route content cases | - | 12/108 |
| Verdict-level change vs old | - | 108/108 NO_ACCEPTABLE_ROUTE unchanged |

Wave 1 made routes structurally representable: 20/108 evaluable cases now emit a routes field with content, and the emission path runs without runtime failure. 88 remain empty and 8 emit junk fragments (document headers like "Hensikt", "Revisjon 30.08.2026", section marks).

## RC-03B - Semantic routing

The 12 content routes do not contain service targets. Inspection of the structured routes shows KB sentence fragments: "Ikke en ensartet tjeneste.", "Barn kan motta samtaler", "Udir kommentar par. 11-6", "ingen foreldretillatelse nodvendig for a kontakte". None matches the frozen acceptable route family. Rendered answers mention a gold-route token in only 9/108 cases; 0 routes carry provenance URLs.

**Route verdicts: 0/108 PASS, unchanged from the old baseline.**

## Structural success does not mask semantic failure

The funnel (routing-funnel.json) shows the gap explicitly:

120 cases -> 108 requiring route evaluation -> 20 structured route produced -> 12 usable content -> 0 provenance URL -> 9 rendered mention -> 0 acceptable target -> 0 route PASS.

## Classification

- **RC-03A (structural): PARTIALLY_EFFECTIVE.** Route emission exists and is stable, but 88/108 still emit nothing and 8 emit junk.
- **RC-03B (semantic): STILL_REQUIRED.** Route-target selection over the KB either does not exist or is not reached. This is the single largest residual mechanism (PW1-R1, 108 criteria) and the highest-leverage next repair.
