# Route-Binding Root Cause (B5 = 23, B4 = 16)

## B5: binding lost at serialization (23 rows)

finalize.py line 191 collapses each evaluable RouteCandidate to
service_type for the canonical routes list. evidence.route_evidence
carries the per-route evidence/provenance join keyed by route_id, but the
frozen scorer consumes routes labels only. Any measurement that asks
"does this route carry its track binding and proof through serialization"
cannot recover the join from the label list.

Binding is complete on the RouteCandidate immediately before finalize
(see route-object-contract-before.md). The repair is therefore additive
serialization, not state reconstruction.

## B4: non-service label mints (16 rows)

Observed Wave 3 labels: "Psykisk helseutredning", "NAV", "Baerum",
"URL", "Ikke en ensartet tjeneste.", "Barn kan motta samtaler",
"ikke hensiktsmessige", "Foreldreansvar bestemmer samtykke", "Akutt fare".

Mechanism: quoted/bold extraction accepts any segment passing
_valid_service_name (length 3-80, no metadata word, no digit). A bold
sentence fragment or an unresolved acronym ("NAV", "URL") passes. The gate
lacks: (a) sentence-fragment rejection, (b) unresolved-acronym rejection.

## Fix direction (Wave 4 Phase A)

1. Generic sentence-fragment gate on the quoted/bold path: reject labels
   whose leading token is a verb/negation marker or which end with
   sentence punctuation (generic marker list, no case strings).
2. Generic acronym gate: reject all-caps labels that carry no resolved
   service identity (unresolved meta-identifiers like "NAV"/"URL" fail;
   documented service acronyms used as service names, e.g. HFU/RPH/DPS/
   "BUP"/"PPT"/"HABU", remain valid targets).
3. Additive structured-route serialization under the evidence map:
   evidence["structured_routes"] carrying route_id, service_identity,
   display_label, track_domain, route_state, access_model, self_referral,
   target_population, scope, evidence_refs, provenance_refs, dims.
   routes stays labels-only.

## Hard Wave 4 gates these address

- 0 route-without-track-binding
- 0 route-without-provenance
- 0 binding-lost-in-serialization
- 0 non-service labels
- 0 rendered-route-without-structured-route

