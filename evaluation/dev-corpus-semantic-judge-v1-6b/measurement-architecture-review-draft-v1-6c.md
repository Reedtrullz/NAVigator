# Measurement Architecture Review - Draft Basis for the Next Stage (V1.6C direction)

Status: **DRAFT_ONLY_NOT_AUTHORIZED**. No implementation, no model calls, no
fixture construction. This document only consolidates authoritative terminal
evidence so the owner can make the architecture decision that
`NEXT_STAGE_REQUIRES_ARCHITECTURE_DECISION = true` requires.

Prepared: 2026-09-12. Lineage state verified at preparation time: A3 engine
`21047fdaaaa4cc28` intact, A4 engine frozen `22a5f61c38b99161` unchanged
post-failure, V1.6B terminal `V1_6B_NO_JUDGE_QUALIFIES` intact.

## 1. Authoritative Evidence Inventory

| Source | Status | Key numbers |
|---|---|---|
| V1.6B candidate comparison (official one-shot screen, 120 fixtures) | TERMINAL | LongCat-2.0 combined 0.8917, MiMo v2.5 Pro combined 0.8917; safety forbidden FN 4 and 5; both fail all 8 gates; no selection |
| V1.6B failure taxonomy (DIAGNOSTIC_ONLY, burned debugging) | DIAGNOSTIC | 15 wrong rows total: 9 shared-identical, 2 shared-split, 4 single-model |
| V1.6B absorbability split (DIAGNOSTIC) | DIAGNOSTIC | 4 form-decidable rows (F-23/26/27, R-11); 1 information gap (R-26); 10 judge-capability rows; absorbing the 4 form rows lifts combined only 0.8917 -> ~0.9167, still failing |
| V1.6B gold-class error matrix (DIAGNOSTIC) | DIAGNOSTIC | Near-perfect on decisive golds (forbidden ABSENT 17/17, uncertainty decisive 9/9); collapse on non-committal golds (critical UNRESOLVED 0/4 and 1/4) |
| V1.6A.4 fresh official one-shot (60 fixtures, SPENT) | TERMINAL FAIL | non-ABSTAIN precision 0.368 vs >= 0.99; 36 false deterministics; 3/60 abstains; 2 evidence-invalid; 0/6 gates |
| V1.6A.4 failure-family analysis | DIAGNOSTIC | 9 families; 20/36 need semantic scope composition/discourse; 16/36 lexeme gaps |
| V1.6A.4 complexity accounting | DIAGNOSTIC | +173 LOC, +8 rules, +22 branches bought TDD wins but no fresh precision |

Provenance split: V1.6B and A4 one-shot numbers are official terminal
results. Taxonomy, absorbability, error-matrix, and family proportions are
diagnostic interpretations of burned/frozen data and are indicative, not
stable estimates.

## 2. What A4 Changed in the Decision Picture

The V1.6B diagnostic recommended two candidate directions: (a) stronger
judge class, or (b) a deterministic boundary extension absorbing the
form-decidable families. A4 executed direction (b) for the assertion-strength
core (hedge/belief/conditional over prohibited claims - exactly the F-23/26/27
pattern) and failed fresh validation decisively: the majority of fresh
failures required operator-scope composition, discourse state, and
multi-signal commitment binding, i.e. semantic interpretation by hand.

Consequence: direction (b) is now evidence-dead at the required precision.
Direction (a) plus information-flow repair is the surviving family of
options. No historical status is rewritten by this conclusion; A4 stands as
`V1_6A4_NOT_READY` with its frozen engine and spent one-shot.

## 3. Structural Diagnosis Across Both Evidence Sets

1. **The bottleneck is calibrated non-commitment, not decisiveness.** Both
   model families are near-perfect when the gold is decisive and collapse on
   UNRESOLVED/ambiguous disposition (V1.6B error matrix) - and A4's
   deterministic layer had the mirror-image failure: it committed instead of
   abstaining (34/36 false deterministics via one catch-all frame rule).
2. **Shared-identical errors across model families** (9 rows) mean an
   ensemble of similar models will not fix the core; the disagreement signal
   lives in the 2 shared-split + 4 single-model rows only.
3. **One row is a pipeline information gap, not a model gap** (R-26): A3
   already grounds service-noun inventory, but those facts are not exposed
   to residual judging.
4. **Deterministic expansion is not a free lever**: each boundary layer so
   far added rules for genuinely lexical boundaries (inventory, clause
   locality, ambiguity abstention) and held precision; assertion strength
   did not, and the next uncovered surface form is always one fixture away.

## 4. Options With Evidence

| Option | Evidence for | Evidence against | Verdict |
|---|---|---|---|
| A. Narrow deterministic scope (lexeme-only subset: unambiguous quotes, explicit retraction, plain attribution verbs) | A4 families F1-F3 are cleanly lexical; A1-A3 pattern worked | Yield on judge residuals unmeasured; A4 showed catch-all default risk; needs new TDD + fresh one-shot; ~0.9167 ceiling from V1.6B absorbability | Conditional, small, only after B if B stalls |
| B. Judge-owned assertion strength + calibration-focused model screening on fresh fixtures | Error matrix: decisive competence exists, non-committal calibration is the failure; 10 judge-capability rows dominate the gap | Requires a stronger/more compliant model class than the two screened; screening cost | **Recommended core** |
| C. Ensemble / adjudication across the two screened families | 2 shared-split + 4 single-model rows could benefit | 9 shared-identical rows immune; both candidates already failed floors; adds protocol complexity | Rejected as primary; only as tie-break diagnostics |
| D. Human-review lane for genuinely ambiguous rows | Honest per contract philosophy | Not automatable scoring; out of scope for a combined scorer | Last resort, not a stage |
| E. Information-flow repair: expose A3 inventory-grounding facts to judge input (R-26) | Deterministic feature that already exists; no new semantics; single-row gap proven on screen | Small measured yield (1 row) | **Recommended companion**, cheap and principled |
| F. Contract/label-room simplification | V1.3 contract heavily iterated; could reduce ambiguity-disposition burden | Historical contract changes are sensitive; gold internally consistent; risk of gate-lowering optics | Rejected for now |

## 5. Draft Recommendation (owner decision required)

**Stage 1 (bounded):** information-flow repair (Option E) - pass
inventory-grounding facts already computed by the A3 layer into the judge
input schema. TDD on fresh fixtures, frozen before run. No assertion-strength
rules, no A5.

**Stage 2 (bounded):** judge-model screening (Option B) with a
preregistered, calibration-weighted scorecard: heavy penalty weight on
non-committal gold rows (UNRESOLVED disposition, hedged forbidden PRESENT),
safety forbidden FN still a hard zero gate, fresh 120-style fixtures frozen
before any run, no best-of-bad selection, max one technical retry policy
frozen in advance.

Ordering rationale: Stage 1 is deterministic, cheap, and removes a known
structural gap before measuring models again; Stage 2 spends model budget
only after the pipeline information is complete. Both stages respect
deterministic-first, fail-closed, fresh-fixture, and no-rewrite principles.
If Stage 2 finds no qualifying model, the honest next step is Option F
(contract simplification review) or Option D - both explicit owner
decisions, not automatic extensions.

## 6. Hard Constraints Carried Into Any Authorized Stage

- Fresh fixtures frozen before any candidate run; burned data only for
  regression/diagnosis.
- Preregistered gates; no threshold derivation on burned or V4 data.
- Disputed official fixture: DISCARD and replace, never repair-in-place.
- No GPT-5.5; subagents per current AGENTS.md delegation policy
  (MiMo/Ling/LongCat/Laguna class, never terra/sol/astra).
- Historical lineages and terminal statuses (V1_6B_NO_JUDGE_QUALIFIES,
  V1_6A4_NOT_READY, RC2_NOT_CERTIFIED, etc.) are immutable.
- One implementation pass plus one bounded bugfix pass per stage, then stop.

## 7. What Remains Unproven

- Yield of Option A on judge residuals is unknown (would need its own fresh
  screen); treated here as conditional only.
- Whether any available model class can pass calibration-weighted floors is
  unknown until Stage 2 runs on fresh data.
- Family proportions from the A4 taxonomy come from one 60-fixture set and
  may shift on new samples.
- The absorbability ceiling (~0.9167) is a diagnostic estimate, not a
  validated projection.

Draft ends. Nothing below this line is authorized or executed.
