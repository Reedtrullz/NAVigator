# RC-08 Postmortem (Retrieval Scoping, Wave 2)

## Status: PARTIALLY_EFFECTIVE

## What improved (from frozen Wave-2 measurement and mechanical diagnostics)
- Provenance-linked claims: 308/645 (47.8 percent) -> 369/625 (59.0 percent).
- Forbidden FAILs: 5 -> 3 (DIS-105 and DIS-116 resolved; both lexical/deterministic).
- Mechanism gates: structured-route-without-provenance 0; no-route consistency mismatches 0.

## What persists
- 103/120 cases still emit 2+ "Nasjonal informasjon" blocks (duplicate/repeated national-information noise unchanged).
- 1 contamination-shaped forbidden FAIL remains (DIS-100, LLM_REVIEWED, PRESENT; cross-contaminated national-information blocks).
- Route-lane outcomes unchanged: 0/108 PASS. Retrieval was not the current route bottleneck.

## Contamination-shaped failures inventory
- Forbidden lane: DIS-100 (PRESENT, contamination-shaped text inside national-information blocks; also failed in Wave 1).
- Forbidden CLAIM_PRESENT deterministic residuals: DIS-119, ROUT-042 (lexical, unchanged from Wave 1).
- Route lane: no contamination-shaped route failures identifiable; route failures are construction-shaped (R0/R1), not contamination-shaped.

## Verdict
RC-08 as implemented is real but bounded. It is NOT the dominant upstream cause of the route funnel; blaming downstream route selection for the R0 gap would be incorrect, but the residual multi-block noise keeps RC-08 relevant. Renderer-level deduplication (RC-06 scope) and the DIS-100 residual are separate follow-ups.
