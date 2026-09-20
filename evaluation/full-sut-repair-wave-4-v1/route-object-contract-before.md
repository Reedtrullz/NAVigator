# Route-Object Contract (Before Wave 4)

Baseline for this task. Frozen Wave 3 candidate state (repaired-sut-manifest
6c1f7d4b...be14f), no edits to that lineage.

## Pre-serialization state

RouteCandidate objects in ctx["_s6_routes"] already carry full binding:

- route_id (R-DOMAIN-NN discovery / R-DOMAIN-KNN national)
- service_type (the route label)
- track_domain, target_population, scope
- five claim dims + route_state
- evidence_refs, provenance_refs, access_model, self_referral

## Serialized state (the B5 break)

runtime/sut/phase3/finalize.py line 191:

    routes = [r["service_type"] for r in evaluable]

The canonical output exposes routes as labels only. Evidence is keyed
separately in evidence.route_evidence by route_id. The frozen scorer
contract consumes routes labels only, so the label-to-track/proof join
is lost at the serialization boundary. Binding exists pre-serialization;
B5 is a labels-only serializer, not a missing binding.

## B4 break

National route targets minted from quoted/bold claims include non-service
labels ("NAV", "Psykisk helseutredning", place names, sentence fragments)
because _national_service_name grounds only on quote/bold marks, with no
service-identity gate beyond length/metadata/digit rejection.

## R0 break

National claims whose text has no quoted/bold/table form yield no route
target at all (84 rows in Wave 3), even when the claim's nearest enclosing
source-doc heading is exactly the service name.

## Contract invariants Wave 4 must preserve

1. routes stays labels-only (frozen scorer contract).
2. Structured route objects may serialize under the open evidence map
   (schema: additionalProperties: true) - no schema file mutation.
3. Fail-closed: unresolvable claims yield no route target.
4. No case IDs, no gold-aware selection, no scorer edits.

