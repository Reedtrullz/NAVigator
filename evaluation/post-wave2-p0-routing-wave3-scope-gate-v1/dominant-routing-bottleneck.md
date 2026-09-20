# Dominant Routing Bottleneck (Wave 2)

Route criteria: 120 total, 108 evaluated, 12 NOT_APPLICABLE. PASS = 0/108.

## Funnel (deterministic classification from frozen predictions + frozen gold)
| Stage | Criteria | Cases |
|---|---|---|
| R0_NO_STRUCTURED_ROUTE | 89 | 89 |
| R1_INVALID_ROUTE_OBJECT | 19 | 19 |
| R2-R10 | 0 | 0 |

- R0 dominates: 89/108 criteria (82.4 percent) come from cases that emit zero structured routes (routes == [], no_route_asserted == true).
- R1: 19 criteria where structured route objects exist but every label is a non-actionable fragment (section headings like "Hensikt", "Status", bare URLs, "Ikke en ensartet tjeneste.", "ikke hensiktsmessige", place names).
- R2-R10: 0 criteria reached these stages in the deterministic pass; deeper semantics cannot be observed until structured actionable targets exist.

## Root cause
The route-proposition construction step (SUT route/answer planner) does not emit structured route targets. RC-07 target selection and RC-10 evidence binding are downstream of this: they cannot rescue cases that never produce a structured target. RC-08 retrieval gates pass, so retrieval scoping is NOT the current bottleneck.

## Owning stage
Route proposition construction in the SUT planner (the component that decides which structured routes to emit and with which evidence binding). Confidence HIGH: predicted routes/no_route_asserted fields are the direct emitted artifact.

## Upstream dependencies
None blocking. RC-08 mechanism gates pass (junk-label gate partial, provenance gates pass). Repair can proceed directly on route construction.

## Wave-3 implication
Primary repair = structured route-proposition construction (actionable targets bound to evidence via shared key). This is the highest-leverage single change: it unblocks 89 R0 criteria and, if fragment labels are replaced by propositions, also the 19 R1 criteria.
