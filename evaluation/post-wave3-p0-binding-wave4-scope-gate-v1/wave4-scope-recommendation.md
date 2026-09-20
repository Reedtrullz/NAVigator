# Wave-4 Scope Recommendation

Task: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY

## Exactly ONE recommended scope

**WAVE4_ROUTE_TARGET_PLUS_BINDING**

## Rationale
- 0 REAL_PRODUCT_SAFETY_REGRESSIONs were found among the 5 P0s (4 AUTHORITY_TRANSITION_CONFOUND + 1 PRODUCT_REPRESENTATION_CHANGE; ROUT-030 = NOT_A_REGRESSION), so WAVE4_SAFETY_FIRST is not triggered and broad safety logic must not be reopened.
- The binding join repair and structured route evaluation are tightly coupled: the serialized labels-only list is invisible to any structured evaluator, and a structured evaluator has nothing to consume without the joined objects. Serialization shape alone changes nothing the frozen scorer can see (0 exact label-gold matches across 39 entries; SemanticJudgeStub.route_equivalent=false). This eliminates WAVE4_ROUTE_EVIDENCE_BINDING_ONLY as a sufficient scope.
- Target semantics and binding are materially coupled: R0_NO_STRUCTURED_ROUTE = 84/108 dominates, and 16/39 entries carry non-service labels (B4_SERVICE_IDENTITY_LOST), so the route-object representation repair inside W4-RC-A must also produce genuine service-identity targets. Both mechanisms block route progress together.
- Uncertainty repair (historical RC-04, 36 PARTIAL) is verified independent of binding, so WAVE4_BINDING_THEN_UNCERTAINTY would smuggle a second workstream into one task.

## Concrete Wave-4 content
- W4-RC-A as the single repair candidate: serializer carries structured route objects (route_id + service identity + evidence_refs + provenance_refs) and the measurement contract consumes joined route objects instead of bare labels; B4 label-quality repair included.
- W4-RC-B and W4-RC-C are explicitly out of scope for the initial Wave-4 authorization.

This recommendation requires explicit owner authorization before any Wave-4 implementation starts.
