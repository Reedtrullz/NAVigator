# RC-06 Assessment: Renderer / Contamination

RC-06 (renderer/answer-quality) was deferred. This assessment separates PRESENTATION_ONLY from MEASUREMENT_RELEVANT effects of the observed contamination and duplication.

## Observed presentation state

| Measure | Wave 1 (old baseline in parens) |
|---|---|
| Answers with 2+ "Nasjonal informasjon" blocks | 104/120 (98) |
| Total national blocks | 645 (610) |
| Max blocks in one answer | 15 (ROUT-093/086/068) |
| Predictions with KB pollution in claims field | 75/120 |
| Predictions with KB pollution in routes field | 2/120 |
| Answer length median / p90 / max | 1879 / 3389 / 4598 chars |

Repeated national-information blocks slightly worsened vs the old baseline while route emission improved; linkage is hypothesis, not proven root cause.

## PRESENTATION_ONLY

Most duplication/noise (repeated national blocks, long answers, irrelevant cross-domain content in rendered text) does not change any frozen scored criterion today: the forbidden_claim dimension only fired 6 times, and route scoring reads the structured routes field. As pure presentation, this is RC-06 territory with moderate product value and low measurement urgency.

## MEASUREMENT_RELEVANT

Contamination crosses into scoring at exactly one point: **the routes and claims fields**. The 12 "content" routes are KB fragments (PW1-R1/B_WRONG_ROUTE_TARGET), and 75 claims fields carry raw KB markdown. The same unscoped retrieval that renders noise also feeds structured fields, which is where route/forbidden criteria read it. This is NOT a renderer defect: the pollution originates upstream (retrieval/aggregation) and the renderer faithfully renders it.

## Classification

**RC-06 as a renderer repair is mostly PRESENTATION_ONLY and should not be prioritized on answer-cosmetics grounds.** The measurement-relevant part of the contamination belongs to an upstream retrieval-scoping repair (new candidate, PW1-R4). Recommend: no renderer-first repair; retrieval scoping first, renderer dedup second, only after checking whether upstream scoping eliminates most duplication.
