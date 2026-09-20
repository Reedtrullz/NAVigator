# V1.6A.4 Final Report - Assertion Strength / Endorsement Strength Grounding

Task ID: `NAV-EXPLORE-DEV-CORPUS-BOUNDARY-V1_6A4-ASSERTION-STRENGTH-GROUNDING`

Authorization: explicit user authorization 2026-09-12
(`/Users/reidar/.codex/attachments/27cd302c-3d50-40b5-909c-ce0db5e81969/pasted-text.txt`,
18 numbered constraints) on top of the audited draft
`evaluation/dev-corpus-semantic-judge-v1-6b/next-task-draft-prompt-v1_6a4.md`.

Terminal status: **`V1_6A4_NOT_READY`**

`NEXT_STAGE_REQUIRES_ARCHITECTURE_DECISION = true`

## 1. What A4 Was Authorized To Test

One last pre-authorized deterministic hypothesis: can assertion strength /
endorsement strength (ASSERTED, HEDGED_ASSERTION, REPORTED_ATTRIBUTED,
QUOTED_ONLY, HYPOTHETICAL_ONLY, NEGATED, SELF_RETRACTED, VAGUE_NONCOMMITTAL,
with ABSTAIN as the uncertain fallback) be extracted deterministically with
very high precision before the semantic judge, so the judge no longer has to
interpret these mechanically observable differences?

A4 was registered as
`V1_6A4_LAST_PREAUTHORIZED_DETERMINISTIC_EXPANSION = true`. No A5/A6 or
further boundary-rule expansion may start automatically, regardless of this
task's outcome.

## 2. Capability Verdict vs Fresh Outcome

The capability proof (`capability-proof.md`) argued the assertion-strength
signal is observable from surface structure (quotes, attribution verbs,
hedges, conditionals, negation, retractions) and therefore deterministic in
principle. Implementation followed, and the layer passed both internal gates
described below.

The fresh official one-shot falsified the precision hypothesis: overall
non-ABSTAIN precision **0.368 (21/57)** against a gate of >= 0.99, with all
6 hard gates failing. The abstraction is real; its surface realization in
ordinary Norwegian text is not capturable at high precision with the
hand-written structural rules this layer is allowed to use.

## 3. TDD Evidence (Fresh Fixtures)

30 fresh TDD fixtures were authored to represent the abstract
assertion-strength mechanism (no text reuse from burned V1.6B cases).

| Phase | Engine | Result |
|---|---|---|
| RED | A3 frozen baseline (`21047fda...`) | 5/30 passed (25 generalized failures reproduced) |
| GREEN | A4 candidate (`22a5f61c...`) | 30/30 passed |

`tdd-red-result.json`, `tdd-green-result.json`, `tdd-fixtures.json`
(`2d096a7d01308a6a8285ce4270bc17f2670c14294238154d8e407f029c43bfc4`).

## 4. Burned Regression Cascade

`run_burned_regressions.py` compared A4 vs A3 on the three legacy dimensions
(route, scope, uncertainty) across all burned sets:

| Burned set | Fixtures | Legacy-dimension mismatches |
|---|---|---|
| burned-120 | 120 | 0 |
| targeted-60 | 60 | 0 |
| official V1.6A2-80 | 80 | 0 |

A4 was strictly additive on every burned input
(`burned-120-regression.json`, `burned-targeted60-regression.json`,
`burned-v1-6a2-80-regression.json`).

## 5. Candidate Freeze Before Fresh Fixtures

The engine was frozen before any fresh official fixture was authored; the
candidate was never queried during fixture authoring.

`candidate-freeze-before-fresh.json` records 8 file SHAs, including:

- Engine `a4_boundary_preclassifier.py`:
  `22a5f61c38b991611b636d24d9a6765f90aa25cf9cc616c5fa0964a770ac5cee`
- A3 baseline engine:
  `21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b` (verified intact)

## 6. Fresh Official Validation Set

Authored blind, then frozen:

| Item | SHA-256 (prefix) |
|---|---|
| `official-validation-fixtures.json` (60) | `b7bc3c39771eb414...` |
| `official-validation-gold-v1_6a4.json` | `69a183c376970756...` |
| `official-fixture-hashes.json` | integrity registry |

Strata: 24 CLEAN_RESOLVABLE, 18 REQUIRED_ABSTAIN (26 expected ABSTAIN total
with adversarial), 18 ADVERSARIAL_MIXED. IDs `OFFA4-CLEAN-01..24`,
`OFFA4-ABST-01..18`, `OFFA4-ADV-01..18`. No disputed fixtures existed;
`DISPUTED_FIXTURES_RETAINED = 0`.

## 7. One-Shot Official Validation Results

`run_official_validation.py` executed exactly once against the frozen
engine. Results in `official-validation-results.json`.

### Overall

| Metric | Value | Gate | Pass |
|---|---|---|---|
| Fixtures | 60 | - | - |
| Non-ABSTAIN decisions | 57 | - | - |
| ABSTAIN decisions | 3 | - | - |
| ABSTAIN rate | 5.0% | - | - |
| Correct | 21 | - | - |
| False deterministics | 36 | - | - |
| Non-ABSTAIN precision | 0.368 | >= 0.99 | FAIL |
| Coverage | 0.950 | - | - |
| Correct coverage | 0.350 | - | - |
| Evidence-span validity | 58/60 | 1.0 | FAIL (CLEAN-16, CLEAN-17 emitted no span) |

### By stratum

| Stratum | N | Abstained | Correct | False deterministics | Precision |
|---|---|---|---|---|---|
| CLEAN_RESOLVABLE | 24 | 0 | 14 | 10 | 0.583 |
| REQUIRED_ABSTAIN | 18 | 2 | 0 | 16 | unsafe non-abstains: 16 |
| ADVERSARIAL_MIXED | 18 | 1 | 7 | 10 | 0.412 |

The failure mode is dominated by over-commitment: the engine resolved
uncertain frames to its single strongest rule (34/36 false deterministics
carry `BC_CLAIM_FRAME_07`) instead of abstaining. One over-abstention
direction also appeared (ADV-01: definitional conditional expected ASSERTED,
got HYPOTHETICAL_ONLY). Clean-stratum correct coverage was 0.583 against the
>= 0.80 gate, so the anti-triviality requirement is also unmet.

## 8. Hard Gate Results (6/6 failed)

| Gate | Required | Actual | Result |
|---|---|---|---|
| Overall non-ABSTAIN precision | >= 0.99 | 0.368 | FAIL |
| Assertion-strength precision | >= 0.99 | 0.368 | FAIL |
| Safety-critical false deterministic | 0 | >0 | FAIL |
| Required-abstain unsafe non-abstain | 0 | 16 | FAIL |
| Clean-resolvable correct coverage | >= 0.80 | 0.583 | FAIL |
| Evidence-span validity | 1.0 | 0.967 | FAIL |

## 9. Failure Taxonomy

`failure-family-analysis.json` classifies all 36 false deterministics plus
the 2 evidence-invalid rows into 9 families, each member exactly once:

| Family | Class | Members | Mechanism (summary) |
|---|---|---|---|
| F1 QUOTE_DELIMITER_COVERAGE | lexical | 3 | ASCII quotes not in QUOTE_MARKERS |
| F2 ATTRIBUTION_ADOPTION_RETRACTION_LEXEME_COVERAGE | lexical | 10 | ifolge, past-tense verbs, hevder, rapporteres, enig i, tok feil, tar tilbake |
| F3 COPULAR_HEDGE_CONSTRUCTION | lexical | 1 | "Det er sannsynlig at ..." |
| F4 NEGATION_MODAL_SCOPE_COMPOSITION | semantic scope | 7 | stacked negation/attitude/modality |
| F5 CONDITIONAL_TEMPORAL_CONSEQUENT_BINDING | semantic scope | 6 | sa snart, hadde vaert rart om, consequent polarity |
| F6 CONTRASTIVE_DISCOURSE_AND_SELF_REVISION | discourse | 2 | men/Eller second-clause updates |
| F7 PARENTHETICAL_ASIDE_SCOPE | semantic scope | 1 | parenthetical first-person assessment |
| F8 ABSENCE_RULE_ORDERING_AND_VAGUE_SURFACE | ordering/semantic | 2 | NOT_PRESENT fires before vague surfaces; no span |
| F9 UNCERTAIN_COMMITMENT_BINDING_COMPOSITE | semantic scope | 4 | multiple weak signals, gold ABSTAIN |

Cross-cutting root causes: (1) a catch-all frame rule defaults uncovered
surfaces to ASSERTED rather than ABSTAIN; (2) A3 lexicons were tuned on
burned surfaces and missed equally ordinary fresh forms; (3) comma-based
clause segmentation separates attribution from claim; (4) 20/36 failures
require operator-scope composition, discourse state, or multi-signal
commitment binding - semantic interpretation; (5) 16/36 are lexeme gaps,
and closing them by enumeration is the whack-a-mole pattern the
authorization forbids.

This artifact is diagnostic only; no rule-per-family patch is proposed or
authorized.

## 10. Complexity Accounting

`complexity-accounting.json` (auth constraint 15). Headline numbers:

| Measure | A3 baseline | A4 added | Combined |
|---|---|---|---|
| LOC | 498 | 173 | 671 |
| Production rules | 29 | 8 | 37 |
| if/elif branches | 68 | 22 | 90 |
| Lexicon lists | 20 | +2 | - |

On development data the layer looked strictly additive and cheap (TDD
30/30, zero burned drift). On fresh data, 5 of 9 failure families require
semantic scope composition rather than more lexemes, and the remaining 4
would need open-ended lexeme enumeration. The marginal deterministic yield
per unit of added rule complexity is inverted relative to the A1-A3 layers,
whose boundaries were genuinely lexical.

## 11. Required Exit Question (auth constraint 14)

> Har A4 redusert semantisk judge-ansvar ved a trekke ut en genuinely
> deterministic feature, eller har vi begynt a implementere semantics by
> hand?

Answer: **`BORDERLINE_SEMANTIC_RULE_SYSTEM`**

Justification from fresh data and rule complexity: the eight-way
assertion-strength abstraction is a coherent, real feature, and the
precision-first design (uncertain -> ABSTAIN) is mechanically sound - the
engine never crashed, registered every outcome, and held the A1-A3 layers
byte-identical. But the fresh one-shot shows the feature's surface
realization cannot be decided by hand rules at the required precision: the
majority of fresh failures need scope composition over stacked negation,
attitude, conditionals, and discourse updates, which is semantic
interpretation implemented by hand. It is not fully
`NOT_DETERMINISTIC_ENOUGH` because a narrower deterministic core (plain
quotes, explicit retraction, clean third-party attribution) demonstrably
works; it is well short of
`GENUINELY_DETERMINISTIC_BOUNDARY_FEATURE` because the remaining rule
mass needed for >= 0.99 precision is exactly the forbidden hand-coded
semantics.

## 12. Protocol Integrity

- One-shot official validation: SPENT. No reruns, no engine patching, no
  gold edits, no fixture replacement after the run.
- Engine frozen at `22a5f61c...` throughout; unchanged post-failure.
- `SEMANTIC_JUDGE_EVALUATION_CALLS = 0` maintained: no judge model (LongCat,
  MiMo, Ling, Laguna, Luna, or other) was invoked as evaluator anywhere in
  A4.
- No V1.6B rescreen was run inside A4 (auth constraint 13).
- No GPT-5.5 was used; no subagents were used.
- Historical PASS statuses (V1.6A/A1-A3) are untouched; burned data was used
  only for regression and diagnosis.

## 13. No-Rescreen Justification

Even though a candidate freeze exists, a combined-pipeline re-screen is not
methodically justified now: the fresh official validation failed all six
hard gates by wide margins (precision 0.368 vs 0.99; 16 required-abstain
unsafe non-abstains vs 0). Screening the judge on top of this layer would
measure a known-broken pre-classifier, and the authorization explicitly
forbids A5-style iteration and rescreen inside A4. The correct next decision
is architectural, not incremental.

## 14. Terminal Status

**`V1_6A4_NOT_READY`** - the hypothesis was implementable, but fresh
precision and utility gates failed. Per the allowed terminal statuses this
is NOT_READY (not INVALID: no protocol, integrity, or contamination
violation occurred).

`NEXT_STAGE_REQUIRES_ARCHITECTURE_DECISION = true`. No A5. No automatic
combined re-screen.

## 15. Recommended Next Step (auth constraint 16)

Measurement architecture review, choosing between at least:

1. Smaller deterministic boundary scope - freeze only the families that are
   genuinely lexical (subset of F1/F2/F3 with strict quote and retraction
   inventories) and route everything else to the judge or abstain.
2. Semantic judge with a simpler label room - move assertion-strength
   interpretation into the judge contract explicitly rather than
   pre-classifying it.
3. Ensemble / adjudication across judge models for the contested boundary.
4. Human-review lane for genuinely ambiguous commitment cases.

Recommendation: option 2 plus a narrowly scoped option 1. The fresh data
shows assertion strength is a semantic dimension; the cheapest honest
architecture is to let the judge own it, while keeping only a tiny
high-precision deterministic guard (explicit retraction markers and
unambiguous quotation) as a pre-filter. Any such change requires a new
explicit task; nothing is started here.

## 16. Residual Limitations

- Failure-family mechanisms are documented at construction level, not
  exhaustively at lexeme level; the enumeration is diagnostic.
- The A4 layer never operated inside the combined pipeline, so downstream
  judge-call reduction claims are untested and remain unproven.
- The one-shot is burned; no further A4 validation can ever be run on this
  fixture set, and no new A4 fixtures may be generated without a new
  architecture decision.
- The failure taxonomy rests on one 60-fixture fresh set; family proportions
  are indicative, not stable estimates.

## 17. Artifact Registry (SHA-256 prefixes)

| Artifact | SHA-256 (prefix) |
|---|---|
| `a4_boundary_preclassifier.py` (frozen engine) | `22a5f61c38b99161...` |
| `candidate-freeze-before-fresh.json` | registry of 8 pre-freeze SHAs |
| `tdd-fixtures.json` | `2d096a7d01308a6a...` |
| `official-validation-fixtures.json` | `b7bc3c39771eb414...` |
| `official-validation-gold-v1_6a4.json` | `69a183c376970756...` |
| `official-validation-results.json` | frozen one-shot output |
| `failure-family-analysis.json` | `98c4031ffefe4c35...` |
| `complexity-accounting.json` | this report's companion |

Report ends. Per auth constraint 18: hard stop. No next stage is started.
