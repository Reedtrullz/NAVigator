# Route Label-to-Evidence Binding Dataflow

Task: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-3 SUT source (runtime/sut/phase2/routes.py, runtime/sut/phase2/pipeline.py, runtime/sut/phase3/finalize.py; SHAs pinned in input-integrity.json), frozen Wave-3 predictions (28 emitting cases / 39 entries), frozen structural-replay-diagnostics.json. Read-only.

## Stage-by-stage trace

1. **Discovery evidence objects.** Each discovery step produces evidence objects (E-DISC-NN / E-DNN ids) with source URLs and per-service facts.
2. **Route object construction (runtime/sut/phase2/routes.py \`build_route_candidates\`, \`build_national_route_candidates\`).** Each route object carries FULL binding: \`route_id\` ("R-<DOMAIN>-NN"), \`service_type\` (the future route label), \`evidence_refs\` (E-D ids from the same discovery step), \`provenance_refs\` (source_url / P-K ids), plus access/condition dimensions. Binding is established here, at object level, before any serialization.
3. **Phase-2 serialization (runtime/sut/phase2/pipeline.py, ~L372-401).** \`route_evidence\` is built keyed by \`route_id\` and placed inside the output's \`evidence\` map. The \`routes\` list itself is serialized as \`[r["service_type"] for r in evaluable]\` - labels only.
4. **Phase-3 finalization (runtime/sut/phase3/finalize.py, ~L232-267).** Identical pattern; the in-code comment states verbatim: "the routes list stays labels-only for the frozen scorer contract."
5. **Measurement observation (evaluation/dev-corpus-scorer-v1/scorer.py \`_score_routes\`).** The scorer reads \`answer["routes"]\` (labels) and \`answer["evidence"]\` separately. \`route_evidence\` is keyed by R-codes; the labels list carries no key. No join path exists between the two structures.

## Precise mechanism

Binding EXISTS inside the serialized output (evidence.route_evidence, 39/39 entries with both evidence_ids and provenance_ids, mechanically verified from structural-replay-diagnostics.json: route_evidence_valid_entries = 39, route_evidence_valid_rule = "R-* entry with both evidence_ids and provenance_ids", cases_with_routes_but_no_provenance = 0). What is absent is the **observable label-to-key join**: the labels list and the evidence dict share no identifier, so Measurement cannot tie a specific route proposition to its supporting evidence.

The 24 emitting routing cases show a perfect 1:1 count correspondence (one route_evidence entry per emitted route object; 32 routing entries of 39 total across 28 emitting cases in three families), confirming the binding is created and serialized - just not joined to the labels the scorer consumes.

## Why "binding = 0/24" is exact but sometimes misread

The claim "label_to_evidence_binding_resolvable_cases = 0/24" is correct at the Measurement-observation layer. It does NOT mean the SUT never attached evidence to routes. The defect is serialization/join-shape, not a total absence of provenance. Prior notes that called this "B3_LABEL_DERIVED_AFTER_BINDING" (labels derived after binding) are a wrong reading: the label and its evidence refs are born together on the same route object; only the serialized shape separates them.

## Gold-side consequence (measured separately)

Even a perfect label-to-evidence join would not flip current route verdicts: \`_score_routes\` matches label strings lexically against gold \`acceptable_routes\`, which are proposition-shaped sentences (e.g. "PPT for pedagogisk utredning", "skolehelsen kan henvise"). Across the 28 emitting cases, label-to-gold correspondence is 0 exact, ~6 token-overlap (ROUT-040/041/052/061/064/068), remainder none. Binding repair and structured route evaluation are therefore coupled: serialization shape alone changes nothing the scorer can see.

