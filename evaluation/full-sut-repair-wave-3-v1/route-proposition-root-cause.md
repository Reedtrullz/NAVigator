# Route-proposition root cause (Wave-2 -> W3-RC-A)

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1 (spec sections 7-8).

## Question

Why do 89/108 route criteria yield no structured route and 19/108
invalid route objects (Wave-2 measurement), and which mechanisms are
proven without opening gold?

## Evidence basis (gold-blind)

- Frozen Wave-2 replay diagnostics + manifests (read-only).
- Live retrieval sampling against the frozen knowledge index
  (load_knowledge/retrieve), e.g. query 'lavterskeltilbud
  kommunepsykolog' returns E-D001 = the raw doc-26 row
  '| Kommunepsykolog/kommunalt lavterskeltilbud | Kartlegging ...'.
- Direct reading of runtime/sut/phase2/routes.py, pipeline.py,
  aggregate.py, phase3/planner.py, render.py, finalize.py (Wave-2,
  sha-pinned in input-integrity.json).
- Doc-26 'Trekkplaster per instans' uses plain-text service names in
  column 1 (no quotes/bold), so the RC-07 quoted/bold-only extractor
  returns None for every identity-table row.

## Classification (spec section 7 taxonomy)

### A. Service candidate never constructed - PROVEN (primary)

_national_service_name() only accepts quoted or bold spans. Table-row
service names are plain text -> no SERVICE CANDIDATE -> no route
proposition -> planner emits INFO-only with no_route_asserted=true.
This explains the empty-route mass without any gold inspection.

### B. Planner ignores existing candidate - PROVEN ABSENT

planner._evaluable_routes consumes every _s6_routes entry in evaluable
states; no filtering beyond route_state. Not a defect.

### C. Planner emits informational claim instead of route - NOT PROVEN

INFO blocks render knowledge claims; the absence of route blocks is
fully explained by A. No separate mechanism needed.

### D. Route target receives raw KB/evidence text - PROVEN (secondary)

The bold path matches markdown front-matter labels ('**Hensikt**:',
'**Formal**:'-class) and doc table fragments containing bold cells,
producing fragment-like route targets (junk routes) in the Wave-2
replay. Confidence: PROVEN as mechanism (regex accepts them);
per-case counts remain gold-blind structural observations.

### E. Access-path object missing - NOT A ROOT CAUSE

RouteCandidate already carries access_verified/contact_verified/
access_model/self_referral. National routes default to UNCLEAR, which
the spec explicitly allows (section 11: do not discard a route because
one optional access detail is unknown).

### F. Route-construction gate too restrictive - PROVEN (same as A)

The quoted/bold-only identity gate rejects every first-column table
service name. This is the normative reading of A for W3-RC-A.

### G. Gate never reached - PROVEN ABSENT

s6_route_reasoning() runs unconditionally for non-suppressed inputs.

### H. Track state resolved before route construction - PROVEN ABSENT

derive_track_state() runs in S8 after S6 and consumes S6 output.

### I. Epistemic state suppresses supported route - PROVEN ABSENT

Routes are never removed by epistemic state; EXISTENCE_ONLY routes
remain evaluable and render with uncertainty wording.

### J. Other - none found beyond A/D.

## Fix direction (bounded, W3-RC-A only)

1. Structured first-column extraction for markdown table-row claims,
   validated against the governing table header so scenario/source-ref
   tables (Situasjon, Paastand, Kommune, 'Jeg ...') can never mint
   route targets. Header resolution reads the frozen source doc via
   the record's source_reference.path (relative to repo root) and
   fails closed: unreadable/ambiguous -> no structured route.
2. Metadata-label reject list on the existing bold path to stop
   front-matter fragments (Hensikt, Advarsel, Revisjon, ...).
3. Keep every frozen contract: gap/historical exclusion, P-K
   provenance numbering, dedupe, track binding, safety suppression.

No implementation is based on LOW-confidence hypotheses; B, C, E, G,
H, I are exonerated by source reading, not by score inspection.
