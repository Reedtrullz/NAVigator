# Annotation summary - RC2 blind set V2 construction

Method: two isolated annotation passes over the retained candidate pool (277 cases), each pass performed by an independent agent with no access to the other pass and no access to RC2 outputs. Pass 2 was model-assisted with GPT-5.6-Luna under the spec 36 firewall (no Blind V1, RC2-regression, or old benchmark examples in prompt context). RC2B-0277 was added to the pool after pass 2 had closed and received a single annotated pass plus adjudication review; agreement metrics are computed on n = 276.

Raw agreement is the mandatory metric (spec 37, target >= 0.90 on all three targets); Cohen's kappa is reported for context. Per-case labels are disclosed only in the sealed answer key.

## Pre-adjudication agreement (pass 1 vs pass 2, n = 276 pool)

| Target | Pool raw agreement | CORE raw agreement (n=159) | CORE kappa |
|---|---|---|---|
| semantic_truth | 211/276 = 0.7645 | 124/159 = 0.7799 | 0.5929 |
| proof_safe | 172/276 = 0.6232 | 124/159 = 0.7799 | 0.5903 |
| product_action | 211/276 = 0.7645 | 124/159 = 0.7799 | 0.5955 |
| All three targets per case (joint) | 169/276 = 0.6123 | 121/159 = 0.7610 | - |

The spec 37 gate (>= 0.90 raw on all three targets) was NOT met. Per spec 37 this mandates an annotation-contract audit rather than blanket adjudication; see final-report.md item 61. The set itself is immutable post-seal (spec 48), so the audit recommendation carries into the next certification phase rather than a V2 edit.

## Disputes and adjudication

97 disagreements were adjudicated in round 1; adjudication reopened a second dispute wave over 106 cases, adjudicated in round 2. All 203 adjudications were resolved against knowledge-base sources and the evaluation contract only; the RC2 evaluator was never consulted. Outcomes across both rounds: 136 pass-1 confirmed, 52 pass-2 confirmed, 15 resolved with new labels. In the CORE 160: 42 pass-1 confirmed, 4 pass-2 confirmed, 1 resolved-new, 113 never disputed. Remaining disputes after adjudication: 0.

Post-adjudication final labels vs pass 2 (pool, n = 276): semantic 220/276 = 0.7971, proof-safe 183/276 = 0.6630, product-action 219/276 = 0.7935. This measures how far adjudication moved final truth from the pass-2 position; it is not the gate metric.

## Plaintext cleanup

Per spec 44, per-case plaintext label artifacts (annotation pass outputs, adjudication files with author labels, and the label-bearing authoring scripts) were deleted after the seal. Aggregate counts in this report and in blind-manifest.json are spec-permitted. The answer key exists only as answer-key.sealed.
