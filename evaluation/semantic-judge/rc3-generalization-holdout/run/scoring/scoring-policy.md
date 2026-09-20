# RC3G Frozen Scoring Policy

Task: `NAV-EXPLORE-RC3-GENERALIZATION-G1_5-SCORING-FREEZE`

Status: `FROZEN_BEFORE_KEY`

## Authority and Scope

The frozen `evaluation-metrics.md` and `proof-soundness-contract-v2.{md,json}` govern G2. This policy adds no gates and removes none. It records rules before truth access. It does not produce a readiness verdict, production certification, truth accuracy, error analysis, or label audit.

All semantic, proof-safe, and product exact metrics use all 159 CORE cases. A runtime failure is incorrect on each exact metric and is counted separately by the runtime gate.

## Prediction Authority

The exact authoritative fields are:

- Semantic: `predictions[].semantic_verdict`.
- Proof-safe: `predictions[].proof_safe_verdict`.
- Product: `predictions[].product_action`.
- Route: `predictions[].route`, reported separately and never substituted for product action.
- Proof objects: `predictions[].proof_object.atom_proofs[]`.
- Atom predictions and evidence state: `predictions[].atom_results[]`, with atom semantic verdict `frozen_verdict`, and `predictions[].atom_results[].proof_state`.
- Atom routes: `predictions[].atom_routes[]`.

Semantic aliases are only `PARTIAL -> PARTIALLY_SUPPORTED` and `INSUFFICIENT -> INSUFFICIENT_EVIDENCE`. `REVIEW_REQUIRED` and `ABSTAIN_INSUFFICIENT` remain distinct. Proof-safe uses the four contract classes. Product actions are exact; `REVIEW_REQUIRED` and `ABSTAIN_INSUFFICIENT` are never merged.

## Auto and Proofs

Only `AUTO_SUPPORTED` and `AUTO_CONTRADICTED` count as auto. The frozen prediction artifact has 24 final auto product cases, `24/159`, or 15.09%. Since the preregistered floor is `>=20%`, the policy records `AUTO_COVERAGE_GATE_PREDETERMINED_FROM_FROZEN_PREDICTIONS`; no threshold, rerun, tuning, or overall readiness verdict follows.

The accepted-proof unit is an atom-level `atom_results[]` entry with `proof_state=ENGINE_PROOF_ACCEPTED`, a matching `atom_routes[]` auto route, and a non-null proof object. It authorizes that atom's final auto route. Compound aggregation can still make the case-level `product_action` review or partial. Prediction-only counts are:

- 137 proof objects emitted.
- 64 structurally valid proof objects and 64 accepted auto atom proofs.
- 32 accepted proofs occur in the 24 final-auto product cases.
- 32 accepted atom proofs are intermediate within non-auto compound aggregation.
- 73 emitted proof objects are non-auto/intermediate because their atom path was not accepted for auto.

Structural validity, evidence groundedness, semantic proof soundness, and proof-safe auto correctness are independent M1-M4 layers. Structural validity uses the frozen contract plus the concrete runtime proof-type registry and exact public source spans. Groundedness requires every proof span, premise, quote, and span id to belong to the authorized public evidence packet. Semantic proof soundness is an atom-level expected proof-safe polarity check. Proof-safe auto correctness is a case-level expected proof-safe polarity check. Auto precision is M4-based, never M1-based.

## Review, Abstain, and Statistics

Necessary review means expected product action is exactly `REVIEW_REQUIRED`. Unnecessary-review rate is predicted review cases whose expected product is not review, divided by all predicted review cases. Abstain recall is exact predicted/expected `ABSTAIN_INSUFFICIENT`. Review-vs-abstain macro F1 uses those two classes across all 159 cases; `AUTO_*` and `PARTIALLY_SUPPORTED` are negative for both. Undefined class precision, recall, and F1 are zero.

Raw counts and exact fractions are authoritative. Wilson intervals use `z=1.96`; display percentages and bounds to two decimals, but compare gates on exact fractions.

Confusion matrices retain every cell. Semantic and proof-safe orders include the full union of truth/prediction labels, including route-only buckets; product order is `AUTO_SUPPORTED`, `AUTO_CONTRADICTED`, `PARTIALLY_SUPPORTED`, `REVIEW_REQUIRED`, `ABSTAIN_INSUFFICIENT`.

## Compound and Subgroups

The 52 compound cases come from public `generalization-cases.json` entries with `compound=true`, not from predictions. The preregistered expected atom denominator is 119; the prediction artifact emitted 224 atoms overall. Atom predictions use `atom_results[].frozen_verdict`. Alignment is exact compatible `atom_id` first, then exact normalized text (`NFKC`, casefold, trim, collapsed whitespace); fuzzy matching is forbidden. Missing expected atoms are incorrect; extra predicted atoms are decomposition errors and cannot be correct. Atom metrics use denominator 119; case-level atom-count and product metrics use 52.

Critical membership is the preregistered public/sealed metadata set of 25 cases. All other subgroup membership must likewise come from preregistration and cannot be chosen after inspecting errors.

## G2 Readiness Logic

`GENERALIZATION_PASS` requires every frozen hard gate to pass. `GENERALIZATION_FAIL` means at least one fails. `GENERALIZATION_INVALID` is reserved for integrity, blindness, or scoring compromise. These are development-generalization statuses, not production certification. The next action is G2's prescribed sequence: verify hashes, authenticated decrypt, structural key validation, mechanical score, freeze the official score, then inspect errors and issue readiness.
