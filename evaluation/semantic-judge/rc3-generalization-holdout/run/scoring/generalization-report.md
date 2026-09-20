# RC3 GENERALIZATION HOLDOUT - G2 REPORT

Task: NAV-EXPLORE-RC3-GENERALIZATION-G2. Blind generalization holdout, RC3G-HOLDOUT-V1 (159 core cases), keyless snapshot NAV-EXPLORE-RC3-GEN-SNAPSHOT-A, frozen predictions, frozen scorer, sealed answer key decrypted in memory after prediction freeze. This is a BLIND GENERALIZATION HOLDOUT result - distinct from the burned V4 shadow and the tuned development runs.

## Verdict

**GENERALIZATION_FAIL** - 11 of 16 preregistered hard gates failed. Official score frozen before any error inspection.

## Headline metrics

| Metric | Result | Gate | Status |
|---|---|---|---|
| Semantic exact | 26/159 = 16.35% (CI 11.41-22.88) | >= 90% | FAIL |
| Proof-safe exact | 44/159 = 27.67% (CI 21.31-35.09) | >= 95% | FAIL |
| Product exact | 60/159 = 37.74% (CI 30.57-45.48) | >= 95% | FAIL |
| Auto coverage | 24/159 = 15.09% | >= 20% | FAIL (predetermined, registered in G1.5) |
| Auto precision | 10/24 = 41.67% (CI 24.47-61.17) | >= 99% | FAIL |
| AUTO_SUPPORTED precision | 7/13 = 53.85% | - | - |
| AUTO_CONTRADICTED precision | 3/11 = 27.27% | - | - |
| Necessary-review recall | 34/44 = 77.27% | >= 95% | FAIL |
| Unnecessary-review rate | 82/116 = 70.69% | <= 15% | FAIL |
| Abstain recall | 16/35 = 45.71% | >= 90% | FAIL |
| Review-vs-abstain macro F1 | 0.520 | >= 0.90 | FAIL |
| Runtime failures | 0/159 | == 0 | PASS |

## Proof metrics (spec 15-19)

| Metric | Count | Gate status (preregistered) |
|---|---|---|
| Proof objects emitted | 137 | - |
| Accepted auto proofs | 64 atoms | - |
| Structurally invalid accepted | 0 | PASS (genuine zero) |
| Ungrounded accepted | 0 | PASS (genuine zero) |
| Semantically unsound accepted | 53 | registered FAIL (see scorer-defect note) |
| Proof-safe unsound autos | 14 cases | registered FAIL (see scorer-defect note) |

Scorer defect: the frozen scorer's four zero-tolerance proof gates cannot fail (denominator-0 short-circuit in gate_results). Recomputed directly from proof_gates counts, semantically unsound accepted proofs (53) and proof-safe unsound autos (14) would both fail. Structural and grounding zeros are genuine. The official score artifact is preserved unpatched; this defect does not change the verdict, which fails on 11 other gates regardless.

## Compound metrics (spec 23-24)

| Metric | Result | Gate | Status |
|---|---|---|---|
| Compound cases | 52 | - | - |
| Expected atoms | 119 | - | - |
| Atom-count exact | 35/52 = 67.31% | - | FAIL |
| Atom semantic exact | 53/119 = 44.54% | >= 90% | FAIL |
| Missing atom rate | 15/119 = 12.61% | - | - |
| Extra atom rate | 2/119 = 1.68% | - | - |
| Top-level aggregation | 29/52 = 55.77% | - | FAIL |
| Compound product exact | 29/52 = 55.77% | >= 90% | FAIL |

## Subgroups (spec 25)

| Subgroup | Semantic | Proof-safe | Product |
|---|---|---|---|
| Critical (25) | 4/25 = 16.0% | 6/25 = 24.0% | 16/25 = 64.0% |
| Track A representative (75) | 13/75 = 17.33% | 22/75 = 29.33% | 16/75 = 21.33% |
| Track B stress (84) | 13/84 = 15.48% | 22/84 = 26.19% | 44/84 = 52.38% |

No subgroup passes. Critical-case product accuracy (64 percent) is materially driven by abstain/route overlap, not by sound autos: auto precision in the critical subgroup is not separately gate-relevant but the overall unsound-auto count dominates the risk picture.

## Confusion summary (spec 26-27)

Full matrices with Wilson 95 percent CIs per cell population are in semantic-confusion.json, proof-safe-confusion.json, and product-confusion.json. Each matrix totals exactly 159.

The central pattern: truth row REVIEW_REQUIRED is empty across all prediction columns in the semantic matrix (0 correct review predictions in semantic space) while the product-level review row recovers 34 of 44. The engine answers "REVIEW_REQUIRED" as its semantic default on novel phrasing; when it does commit, it is wrong more often than right.

## What generalized and what did not (spec 40)

| Capability | Generalized? | Evidence |
|---|---|---|
| Proof soundness (semantic layer) | NO | 53 unsound accepted atoms out of 64 |
| Structural validity / grounding | YES (held) | 0 structural invalids, 0 ungrounded across 64 accepted proofs |
| Auto precision | NO | 41.67 percent vs 99 percent gate |
| Routing | NO | coverage 15.09 percent, unnecessary review 70.69 percent |
| Abstention | NO | recall 45.71 percent, macro F1 0.520 |
| Compound decomposition | NO | atom-count exact 67.31 percent, atom semantic 44.54 percent |
| Semantic/proof/product exactness | NO | 16.35 / 27.67 / 37.74 percent |

## Answer to the generalization question

The Phase A/B/C improvements did NOT generalize to a fresh, untuned corpus. The deterministic proof scaffolding (structural validation, span grounding, zero runtime failures) transferred; the semantic judgment, decomposition coverage, and routing calibration did not. RC3's development gates were met on tuned development data but the architecture is not yet robust to natural distribution shift.

## Next-R&D decision (spec 41 decision tree)

Proof soundness and auto precision both fail heavily, so per the preregistered tree: **next R&D must continue repairing the proof architecture first** - specifically the semantic-soundness validator (negation/deontic scope at atom level) and the decomposition stage - before routing/calibration work can be meaningful. Routing repair alone would push unsound autos into production.

No patches, no reruns, no tuning, no new blind set in this task. All findings feed a future R&D task.
