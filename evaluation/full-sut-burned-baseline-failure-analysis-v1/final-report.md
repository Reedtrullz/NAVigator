# Final report - NAV-EXPLORE-FULL-SUT-BURNED-BASELINE-FAILURE-ANALYSIS-V1

Created: 2026-09-16T02:03:33+02:00
Mode: READ-ONLY analysis. No SUT, gold, measurement, or prediction changes.
Baseline: MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED
Classification: BURNED_DEV_BASELINE_ONLY. Not certification, not fresh evidence, not production readiness.

## 1. Input integrity

- Repair lineage hashes: 14/14 pins OK (shasum -a 256 -c from repo root).
- Old residual-human-adjudication lineage: 16/16 pins OK.
- All pins, constraint attestations, and known reference SHAs: baseline-integrity.json.
- SUT_CHANGES = 0, GOLD_CHANGES = 0, MEASUREMENT_CHANGES = 0, PREDICTION_RERUN = 0.

## 2. Baseline results (frozen semantics, 600 criteria / 120 cases)

| Bucket | Count |
|---|---|
| FAIL | 227 |
| UNRESOLVED (fail-closed) | 5 |
| DEGRADED (PARTIAL uncertainty 34 + evidence<1.0 38) | 72 |
| PASS | 284 |
| CRITERION_ABSENT (NOT_REQUIRED / route NOT_APPLICABLE) | 12 |

Fail rate over the 588 criteria with an applicable verdict: 38.61 percent.

Per dimension:
- critical_condition: 111 FAIL / 5 UNRESOLVED / 4 PASS.
- forbidden_claim: 6 FAIL / 114 PASS.
- route_correctness: 108 FAIL / 12 NOT_APPLICABLE (gold defines no acceptable_routes).
- required_uncertainty: 2 FAIL (VIOLATED) / 34 PARTIAL / 84 PASS (incl. 83 NOT_REQUIRED + 1 SATISFIED).
- evidence_completeness: mean 0.6833; 82 fully complete, 38 degraded.

Per scenario family (fails): routing 137, discovery_adversarial 49, safety 41.
Per authority (fails): DETERMINISTIC 223, LLM_REVIEWED 3, LLM_ADJUDICATED 1.
Case level: 112/120 cases have at least one failing criterion; 8 have none.

## 3. Failure inventory

failure-inventory.json lists 304 entries: 227 FAIL, 5 UNRESOLVED, 72 DEGRADED,
each with case, criterion, dimension, verdict, authority, evidence, gold criterion,
SUT answer excerpt, execution status, priority gold/SUT, and a likely owning stage.
No fixes proposed at inventory level (task order respected).

## 4. Failure families (failure-families.json)

- F1_SAFE_TRIAGE_COLLAPSE: 19 priority mismatches; 17 of 19 collapse to ACUTE_RISK_NOW, 2 to URGENT_NOT_ACUTE; 5 sit on EXECUTION_FAILED cases. Confidence HIGH at output level.
- F2_PREMATURE_ABSENCE_NO_ROUTE: universal; all 120 predictions have routes=[] and no_route_asserted=true while prose carries routes; drives 88 PREMATURE_ABSENCE + 108 NO_ACCEPTABLE_ROUTE. Interface-level OBSERVED; upstream cause hypothesis MEDIUM (discovery_invoked=0).
- F3_INPUT_SCHEMA_REJECTION: 9 EXECUTION_FAILED via sut-input/v1 unknown profile fields / age type; proven root cause; contaminates F1/F2.
- F4_PROVENANCE_EVIDENCE_GAPS: SOURCE_URL_REQUIRED_MISSING 1, PROVENANCE_CHAIN_BROKEN 2, 38 evidence rows below 1.0; 291/610 claims provenance-linked; empty structured provenance arrays.
- F5_CLAIM_ASSERTION_DEFECTS: 6 forbidden FAILs; 5-6 likely genuine assertions (5 LLM-confirmed, DIS-105 literal ROUTE_FULLY_VERIFIED block); ROUT-042 is a suspected negation false positive of the frozen lexical rule (ROOT_CAUSE_HYPOTHESIS; LABEL_SENSITIVITY_ONLY framing, no gold change proposed).
- F6_UNCERTAINTY_UNDER_EXPRESSION: 2 VIOLATED on failure path (SAF-009/SAF-019 emit uncertainty_expressed=[] despite known profile gaps); 34 PARTIAL.
- F7_PRESENTATION_NOISE: 98/120 answers with >=2 repeated national blocks; 23 with cross-domain finance/tax material; 1 with evaluation meta-text; 111/120 with fixed no-offers disclaimer; 98 presented_as_complete with recoverable failures.
- F8_SEMANTIC_LANE_UNRESOLVED: 5 unmapped critical conditions fail-closed UNRESOLVED; expected contract behavior, not a defect.

OBSERVED_FAILURE vs ROOT_CAUSE_HYPOTHESIS separation is recorded per family in failure-families.json.

## 5. Safety-critical analysis

safety-critical-analysis.md. Headline: 19/20 safety priority classes wrong
(over-escalation and coarse classes, zero under-escalation observed on acute-risk
gold), 20/20 structured routes failed, worst evidence completeness of all families
(0.15). No P0 observed in frozen verdicts; the P0-shaped hypothesis (renderer
relying on empty structured routes) is explicitly marked as hypothesis.

## 6. Presentation vs semantic

presentation-vs-semantic-analysis.md. Presentation defects drive zero frozen
verdicts. The dominant product defect is the prose/structured divergence: useful
content exists in prose but the machine-readable contract is empty or default.
Two items are measurement-side: 5 UNRESOLVED rows and the suspected ROUT-042
false positive.

## 7. Severity (engineering triage, not a measurement score)

- P0: none observed.
- P1: 19 priority mismatches; 108 route fails; 88 absence claims; 6 forbidden; 2 uncertainty violations.
- P2: 38 evidence-incomplete rows; 5 unresolved rows (contract fail-closed).
- P3: duplication, cross-domain material, meta leakage, disclaimer juxtaposition.

## 8. Repair candidates (RC-01..RC-06) and priority

repair-candidates.json / repair-priority.md. Recommended order:
1. RC-01 input schema extension (unblocks 9 cases, proven cause).
2. RC-02 triage classifier granularity (safety, with mandatory safe fallback).
3. RC-03 structured routes/provenance population (breadth: up to 196 criteria share the root).
4. RC-04 failure-path uncertainty emission.
5. RC-05 evidence completeness assembly.
6. RC-06 renderer cleanup.
Nothing is implemented. Measurement-contract changes and any case-specific logic are explicitly out of scope.

## 9. Anti-overfitting

No proposed fix references burned case IDs or corpus literals in runtime logic.
Case-specific negation handling is marked OVERFIT_RISK in repair-candidates.json
and not recommended. The ROUT-042 finding is documented as LABEL_SENSITIVITY_ONLY.

## 10. Deliverable hashes (self-pin, generated after writing)

See hashes section in TASK-LOCK.json / task-lock notes; each deliverable SHA-256
is recorded in the lineage directory manifest below.

## 11. Terminal status

FULL_SUT_BURNED_BASELINE_FAILURE_ANALYSIS_COMPLETE

Hard stop: no fixes implemented, no fresh holdout, no SUT changes.
