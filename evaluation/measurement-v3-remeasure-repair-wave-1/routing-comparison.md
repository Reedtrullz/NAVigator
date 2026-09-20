# Routing Comparison - Wave-1 vs Old Burned Baseline

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1

Comparison scope: frozen Wave-1 v2 predictions (structural-120-replay-v2) versus MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED, using the frozen Measurement V3 stack. Read-only post-freeze analysis.

## Structured route emission (RC-03)

Old phase-3 predictions: 0 of 120 cases carried non-empty structured routes; no_route_asserted was true on all 120.

New Wave-1 predictions: 23 cases carry non-empty routes (30 entries, 13 distinct labels); no_route_asserted true on 97 of 120.

Route-gaining cases: DIS-106, DIS-114, ROUT-022, ROUT-026, ROUT-029, ROUT-031, ROUT-032, ROUT-039, ROUT-047, ROUT-049, ROUT-050, ROUT-052, ROUT-057, ROUT-063, ROUT-065, ROUT-066, ROUT-068, ROUT-069, ROUT-070, ROUT-072, ROUT-073, ROUT-088, SAF-019.

Distinct route labels: "Ikke en ensartet tjeneste.", "Revisjon 30.08.2026", "Barn kan motta samtaler", "Diagnostisk utredning (nevropsykiatrisk)", "Hensikt", "gratis", "BUP-fristbrudd", "12-16 år kan samtykke til helsehjelp i forhold foreldrene ikke er informert om", "§ 10", "ingen foreldretillatelse nødvendig for å kontakte", "Praktisk betydning for skolehelse", "PRL § 4-4", "Udir kommentar §11-6".

Label quality note: most labels are document section headers, legal references, or source annotations rather than service names. Structured route emission exists and is provenance-linked, but label semantics are still not service-identity quality. This is a future repair candidate observation, not a scored criterion change.

## Consistency and provenance

- 0 consistency mismatches (every case with non-empty routes has no_route_asserted false).
- 0 routes without provenance.
- PREMATURE_ABSENCE evidence flags fell from 88 to 69 rows; the 19 lost flags are exactly the route-gaining cases.

## Route verdicts

Unchanged: 108 of 108 scored route criteria remain NO_ACCEPTABLE_ROUTE; 12 remain NOT_APPLICABLE. The routing dimension produced 0 verdict-level improvements and 0 regressions.

The 13 old CRITICAL_ERROR critical-condition verdicts that were PREMATURE_ABSENCE artifacts of empty routes moved laterally to fail-closed states:

- 6 deterministic: NO_CRITICAL_ERROR -> UNRESOLVED state (DIS-106, ROUT-063, ROUT-065, ROUT-069, ROUT-070, ROUT-073).
- 7 LLM_REVIEWED: UNRESOLVED verdict/state (ROUT-031, ROUT-032, ROUT-039, ROUT-049, ROUT-057, ROUT-066, ROUT-072).

These are fail-closed lateral moves, never scored as improvements.

## Report-only anomalies

- DIS-106 and ROUT-069 route rows carry empty evidence arrays in the new measurement where the old rows carried the PREMATURE_ABSENCE flag. Verdict impact: none (both remain NO_ACCEPTABLE_ROUTE). Classification: REPORT_ONLY.

## Interpretation boundary

BURNED_DEV_BASELINE_ONLY. Structural route improvements are mechanical facts about the frozen candidate; they did not change any authoritative route verdict and are not certification, production readiness, or generalization evidence.
