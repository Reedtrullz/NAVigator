# Epistemic Consequences of Route/Evidence Binding

Task: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY
Basis: p0-regression-diagnosis.json, authority-transition-confounds.json, rout-069-analysis.md, route-binding artifacts (this task); frozen Wave-2/3 measurements. Read-only.

## Question
Does route/evidence binding failure cause downstream no_route_asserted, PREMATURE_ABSENCE, uncertainty PARTIAL/VIOLATED, or unresolved route state?

## Findings by state

### no_route_asserted (P0 cases ROUT-022/031/033/047)
Wave-3 RC-07 heading suppression removed the Wave-2 pseudo-routes (markdown heading tokens such as Hensikt/Status leaking as route labels). The pseudo-routes were construction artifacts, never real route objects: no evidence was ever bound or lost, and nothing reached the serialization layer. NOT binding-caused.

### PREMATURE_ABSENCE / uncertainty observations on the P0 cases
With routes=[] the generic R3 rule (PREMATURE_ABSENCE) fires in _score_critical BEFORE condition mapping, and none of the four free-text conditions (ROUT-022/031/033/047) exist in CRITICAL_CONDITION_MAP (scorer L33-41). The resulting PARTIAL / absence observations are measurement artifacts of pseudo-route removal plus scorer rule ordering - UPSTREAM_BINDING_CAUSED = NO for all four.

### ROUT-069
condition=null -> Wave-2 NO_CRITICAL_ERROR vs Wave-3 CRITICAL_ERROR; owner DETERMINISTIC in both waves. PRODUCT_REPRESENTATION_CHANGE. Not binding-caused.

### Emitting route cases (28 cases / 39 entries)
no_route_asserted=false; route verdicts FAIL through lexical label-vs-proposition matching. A perfect binding join alone flips nothing (0 exact label-gold matches across 39 entries; SemanticJudgeStub.route_equivalent=false). Binding is a measurement-observability defect here, not the cause of the FAILs.

### Historical RC-04 uncertainty-depth (36 PARTIAL)
INDEPENDENT_RC04_UNCERTAINTY_DEFECT: originated in Wave-2 uncertainty-depth grading, untouched by the routing waves, unaffected by binding serialization.

### UNRESOLVED (18 criteria)
No trace to binding in the frozen artifacts; separate measurement layer.

## Conclusion
- Criteria with epistemic states caused by binding failure: 0.
- INDEPENDENT_RC04_UNCERTAINTY_DEFECT: remains (historical 36 PARTIAL).
- Broad uncertainty repair must NOT be coupled to the binding repair; it is deferred as independent candidate W4-RC-C.
