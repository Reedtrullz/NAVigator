# RC-07 Effect Analysis - Route Target Selection

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-2 measurement, frozen Wave-1 measurement, frozen Candidate-2 structural replay diagnostics. See routing-funnel.json for the machine-readable funnel.

## Funnel comparison (route criteria)

Stage | Wave 1 | Wave 2
--- | --- | ---
Route criteria total | 120 | 120
Route-evaluated | 108 | 108
Structured route present (cases) | 20 | 20 (24 entries, 14 distinct labels)
Junk-like route entries | not quantified W1 | 15/24 (Hensikt x6, "Ikke en ensartet tjeneste." x2, "ikke hensiktsmessige" x2, URL x2, Status, Bærum, Meldeplikt)
Fragment-like route labels | not quantified W1 | 2 (routing/ROUT-072, routing/ROUT-083; diagnostic examples only)
Provenance valid | not gated W1 | 20/20 cases (gate PASS)
Target relevant to active track | not quantified W1 | 0 resolvable (see below)
Target supported by evidence | not quantified W1 | 0 resolvable (see below)
Acceptable route family match | 0 | 0
Final route PASS | 0 | 0
Final route FAIL | 108 | 108

Wave-1 reference funnel: 120 -> 108 route-evaluated -> 20 structured -> 12 plausibly usable -> 0 PASS.

## Mechanism finding: label-to-evidence mapping is unresolvable

In all 20 structured-route cases, route labels cannot be mapped to their supporting evidence: the frozen prediction field evidence.route_evidence is keyed by R-codes (for example R-MENTAL_HEALTH-K01 -> E-D004 / P-K004), not by route label string. Route labels are frequently fragments ("Hensikt", bare URLs) rather than identifiable service targets. Evidence-support of a target is therefore mechanically unresolvable 20/20, independent of whether the underlying evidence exists.

RC-07 moved the bottleneck: provenance existence is no longer the blocking gate (20/20 valid); route label identity, target selection quality, and label-to-evidence binding are.

## Explicit inspection of remaining fragment-like labels

- routing/ROUT-072: labels ["Hensikt", "Praktisk betydning for skolehelse", "URL"] - section headings and a URL, not actionable service targets.
- routing/ROUT-083: labels ["URL"] - a bare URL, not an identifiable route proposition.

These are diagnostic examples of the general fragment-label pattern (15/24 junk-like entries). No runtime behavior was derived from these case IDs.

## RC-07 verdict

No route criterion improved semantically: route verdict distribution is identical to Wave 1 (108 NO_ACCEPTABLE_ROUTE, 12 N/A). RC-07 as implemented did not achieve semantic route-target recovery. The remaining bottleneck is structural: route labels must become full target propositions bound to their evidence entries by a shared key before acceptable-family matching can operate.
