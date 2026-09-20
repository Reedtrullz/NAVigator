# Retrieval Contamination Analysis

## Scope

Cross-layer contamination audit over the frozen Wave-1 120-case predictions, recomputed by build_analysis.py from the pinned measurement freeze (SHA 1f4aac89aa90...e5e7c1). Read-only; no SUT, gold, or measurement changes.

## Layer counts (frozen Wave-1 predictions)

| Layer | Contaminated | Total | Detail |
|---|---|---|---|
| Rendered answers | 104/120 | 120 | 2+ "Nasjonal informasjon" blocks each; 645 national blocks total; max 15 blocks in one answer |
| Claims field | 75/120 | 120 | KB-markdown fragments leaked into structured claims |
| Routes field | 2/120 | 120 | KB fragments instead of service targets (B_WRONG_ROUTE_TARGET) |
| Answer length | median 1879.5 chars, p90 3398, max 4598 | | Inflated by unscoped national blocks |

## Cross-layer mechanism

All three structured/rendered output layers (answers, claims, routes) receive material that no per-case scoping or track filter removed. This is consistent with a single shared retrieval/aggregation mechanism upstream of rendering:

- Forbidden-claim residual: 6/6 failures place the prohibited content inside an unattributed "Nasjonal informasjon" block (see forbidden-claim-analysis.md). The product's own voice asserts none of them.
- Route classification: the 12 B_WRONG_ROUTE_TARGET routes contain KB sentence fragments ("Ikke en ensartet tjeneste.", "Barn kan motta samtaler"), not service targets.
- Evidence attachment: 15 NO_PROVENANCE_ENTRIES cases have no provenance to attach, consistent with retrieval never binding case-relevant sources.

## Observed vs hypothesis

- OBSERVED_FAILURE: 104/120 polluted answers, 75/120 polluted claims, 2/120 polluted routes, 6/6 forbidden residual contamination.
- ROOT_CAUSE_HYPOTHESIS: one shared unscoped-retrieval/track-filtering defect upstream of answer assembly, evidence attachment, and route emission. MEDIUM confidence on the exact owning stage (track filtering vs aggregation vs composition); HIGH confidence the mechanism exists and is shared, because pollution appears simultaneously in all three layers.

## Consequences for repair sizing

- A retrieval-scoping repair addresses the entire residual forbidden-claim set (5/6 product-side; ROUT-042 is LABEL_SENSITIVITY_KNOWN and excluded from sizing), the route-fragment pollution, and the 15 NO_PROVENANCE_ENTRIES evidence sub-case, without forbidden-claim-specific or case-specific logic.
- The 23 PROV_HAS_URL_NOT_ATTACHED evidence cases are a separate attachment defect downstream of retrieval (see PW1-R5 in residual-failure-families.json) and remain repairable standalone.

## Measurement note

Contamination is here an engineering observation; Measurement V3 scores it only where frozen criteria (forbidden_claim, route_correctness, evidence_completeness) intersect it. No new measurement dimensions are proposed in this read-only task.
