# Route-proposition dataflow BEFORE W3-RC-A (Wave-2 baseline)

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1 (spec sections 6-8).
All observations are from frozen Wave-2 source and live replay inputs read
2026-09-16; no gold was opened.

## Stage-by-stage trace (Wave-2 path)

1. Input normalization (runtime/sut/context.py)
   - input: raw user query + profile + location_context
   - output: normalized DecisionContext
   - track binding: none yet; evidence binding: none
   - route semantics: none (correct at this stage)

2. Safety triage S2 (runtime/sut/phase2/safety.py)
   - output: priority, signals, suppressed_routing
   - suppressed_routing=true short-circuits S3; acute cases never get
     tracks or routes by safety precedence (invariant, not a defect).

3. Track decomposition S3 (runtime/sut/phase2/decompose.py)
   - output: active tracks with domains
   - route semantics: none (correct)

4. Knowledge retrieval S4 (runtime/sut/phase2/knowledge.py)
   - input: query per track domain; output: max 5 records per domain,
     record.claim = ONE verbatim span (line or sentence slice)
   - record = KNOWLEDGE RECORD only; no service identity object exists
   - Because _iter_spans yields whole lines, doc-26 table rows are
     retrieved verbatim, including the leading '| Instans | ...' cell.
   - LOSS POINT: a service name inside a table row is never lifted into
     a structured service candidate.

5. Local discovery S5 (runtime/sut/phase2/discovery_adapter.py)
   - output: per-track discovery steps with structured services
     (name, access_methods, target_group, source_url, self_referral)
   - This is the ONLY stage that produces SERVICE CANDIDATE-shaped
     objects, and only when the V2.4 provider completes. Without a
     completing provider the step yields state != COMPLETED and zero
     services.

6. Route reasoning S6 (runtime/sut/phase2/routes.py)
   - build_route_candidates(): discovery services -> RouteCandidate
     (five claim dimensions; state from _route_state)
   - build_national_route_candidates(): scans S4 records;
     _national_service_name() accepts ONLY quoted 'name' or **bold**
     segments (3-80 chars, no digits/|/#).
   - LOSS POINT A (PROVEN): doc-25/26 service tables use plain text in
     the first column (Fastlege, Skolehelsetjeneste, HFU,
     Kommunepsykolog..., BUP (spesialisthelsetjenesten), HABU ...).
     No quotes, no bold -> extractor returns None -> zero national
     routes for most queries.
   - LOSS POINT D (PROVEN): the bold path accepts front-matter labels
     such as **Hensikt** / **Formal** -> raw fragment becomes a route
     target (junk route labels observed in Wave-2 replay artifacts).

7. Evidence aggregation S7 (runtime/sut/phase2/aggregate.py)
   - build_claims() materializes one claim per route dimension; a route
     with no evidence_refs gets authority NONE.
   - knowledge_fact claims carry the verbatim span separately.

8. Epistemic assignment S8
   - derive_track_state(): S4-records-only track => EXISTENCE_ONLY
     ceiling; EXISTENCE_ONLY routes keep per_track EXISTENCE_ONLY.

9. Answer planning S9 (runtime/sut/phase3/planner.py)
   - _evaluable_routes() filters route_state in (FULLY_VERIFIED,
     ACCESS_PARTIAL, EXISTENCE_ONLY) from ctx['_s6_routes']
   - With zero national routes, PRIMARY/SECONDARY_ROUTE blocks are
     never emitted; no_route_asserted=true while INFO blocks still
     render the knowledge claims.
   - presented_as_complete requires all per_track states evaluable.

10. Rendering S10 (runtime/sut/phase3/render.py)
    - _route_line() resolves route ids from the plan; wording per
      route_state; renderer creates no route semantics (correct).

11. Finalize S11 (runtime/sut/phase3/finalize.py)
    - routes = evaluable labels; consistency checks:
      plan-routes-in-structured, labels-substring-of-answer,
      span-refs-resolve; route_evidence map built from evaluable
      routes.

## Where route semantics are currently absent or lost

- S4 -> S6 boundary: table-row service identities never become SERVICE
  CANDIDATEs (root cause of R0 empty-route cases).
- S6 bold path: front-matter labels leak in as junk targets (R1
  invalid-object cases).
- Downstream stages (S7-S11) faithfully consume whatever S6 produced;
  no additional loss points found.

## Object-type accounting (spec section 8)

- KNOWLEDGE RECORD: _s4_records (verbatim claim spans)
- EVIDENCE: evidence_ids on records/routes/claims
- SERVICE CANDIDATE: discovery services only (S5); national services
  have no candidate representation before S6
- ROUTE PROPOSITION: RouteCandidate objects in _s6_routes
