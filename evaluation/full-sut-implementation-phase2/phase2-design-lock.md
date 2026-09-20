# Phase 2 Design Lock

Status: FROZEN_DESIGN. This document freezes the Phase 2 architecture before
implementation. Changes after implementation start require a terminal stop
and a new lineage.

## 1. Source lineage

New package runtime/sut/phase2/. Phase 1 files under runtime/sut/ stay
byte-identical (verified against the phase1-source-snapshot). The Phase 2
pipeline composes the Phase 1 context, schemas, and fail-closed accounting;
it does not fork them.

## 2. Module layout

| Module | Stage | Responsibility |
|---|---|---|
| phase2/safety.py | S2 | Load data/safety-triage-rules-v2.json, evaluate 12 internal classes with precedence and negation guard, collapse to canonical 3-enum. |
| phase2/decompose.py | S3 | Deterministic domain tracks (conjunctive splitting, conservative single-track fallback). |
| phase2/knowledge.py | S4 | Structured retrieval over data/knowledge-index-v1.json; verbatim spans from source docs; GAP_REGISTER never positive evidence; HISTORICAL_RESEARCH never sole route authority. |
| phase2/discovery_adapter.py | S5 | Thin adapter over runtime/discovery/orchestrator.run_discovery (replay); NOT_APPLICABLE on absent municipality; FC-03 mapping. |
| phase2/routes.py | S6 | RouteCandidate construction; five claim dimensions separate; downgrades only; eligibility rules from data/rules-v1.json as additional evidence. |
| phase2/aggregate.py | S7+S8 | claim -> evidence -> provenance wiring, conflict registration, conservative epistemic collapse, execution status. |
| phase2/pipeline.py | S1-S11 | Composition + provenance records + structured Phase-2 answer placeholder; preserves the INTERFACE_GAP-001 mapping from Phase 1 S11. |

## 3. Safety rules V2 (new frozen data file)

data/safety-triage-rules-v2.json extends (never mutates) the frozen V1
vocabulary. V1 files are untouched. V2 adds:

- Full coverage of the 20 burned safety corpus utterances via the frozen
  architecture's sanctioned internal 12-value safety_class taxonomy
  (ACUTE_RISK_NOW, ACUTE_RISK_HIGH, ACUTE_SOMATIC_MEDICAL,
  ACUTE_RISK_UNSURE_TRIAGE, ACUTE_RISK_HIGH_THIRD_PARTY,
  SAFETY_CONCERN_NO_ACUTE_VIOLENCE, NON_ACUTE_ROUTINE,
  URGENT_PSYCHOSIS_SUSPECT, ABUSE_DISCLOSURE_REPORTING,
  SAFETY_CONCERN_REPORTING, URGENT_CARE_CAPACITY, SYSTEM_SAFETY_PRECEDENCE).
- Negation guard: an acute signal match is discarded when the same clause
  negates it ("ikke ... akutt", "ingenting er akutt", "ikke farlig"). The
  guard itself is regression-tested; unmatched negation handling stays a
  documented limit.
- Emergency route vocabulary (113/116 117/116 123/116 111/116 006/112)
  copied from V1, used for acute-route evidence.

Internal safety_class collapses to the canonical output 3-enum:

| Internal class | Output priority | suppressed_routing |
|---|---|---|
| ACUTE_RISK_NOW, ACUTE_RISK_HIGH, ACUTE_SOMATIC_MEDICAL, ACUTE_RISK_HIGH_THIRD_PARTY | ACUTE_RISK_NOW | true |
| ACUTE_RISK_UNSURE_TRIAGE | ACUTE_RISK_NOW | true |
| URGENT_PSYCHOSIS_SUSPECT, ABUSE_DISCLOSURE_REPORTING, SAFETY_CONCERN_REPORTING | ACUTE_RISK_NOW | true |
| URGENT_CARE_CAPACITY, SAFETY_CONCERN_NO_ACUTE_VIOLENCE | URGENT_NOT_ACUTE | false |
| SYSTEM_SAFETY_PRECEDENCE | URGENT_NOT_ACUTE | false |
| NON_ACUTE_ROUTINE | NOT_ACUTE | false |

Amendment (2026-09-14, pre-implementation, documented before any code):
SAFETY_CONCERN_REPORTING moves from the ACUTE_RISK_NOW row to the
URGENT_NOT_ACUTE row. Rationale: a safety concern with a reporting pathway
but no acute violence signal (corpus shape SAF-012) is urgent-not-acute;
cases where the utterance itself carries an acute signal (violence, abuse,
care collapse) are raised by their own signal class, not by this default.
ABUSE_DISCLOSURE_REPORTING remains ACUTE_RISK_NOW (explicit disclosure of
violence/abuse against a child: safety action first). Final table:

| Internal class | Output priority | suppressed_routing |
|---|---|---|
| ACUTE_RISK_NOW, ACUTE_RISK_HIGH, ACUTE_SOMATIC_MEDICAL, ACUTE_RISK_HIGH_THIRD_PARTY, ACUTE_RISK_UNSURE_TRIAGE | ACUTE_RISK_NOW | true |
| URGENT_PSYCHOSIS_SUSPECT, ABUSE_DISCLOSURE_REPORTING, SYSTEM_SAFETY_PRECEDENCE | ACUTE_RISK_NOW | true |
| URGENT_CARE_CAPACITY, SAFETY_CONCERN_NO_ACUTE_VIOLENCE, SAFETY_CONCERN_REPORTING | URGENT_NOT_ACUTE | false |
| NON_ACUTE_ROUTINE | NOT_ACUTE | false |

Rationale: any unresolved or high-risk safety state fails closed to the
acute path; safety never degrades because decomposition found other domains.

## 4. Track decomposition (S3)

- Domains: the frozen context schema enum (mental_health, housing,
  financial_support, child_safety, education, employment, legal_rights,
  general).
- Deterministic keyword splitting: explicit conjunctions and topic markers
  produce multiple tracks only when distinct need domains are recognized;
  otherwise one track (conservative).
- Each track records needs_local_discovery and its triggering reason.
- Track priority: safety first (guaranteed by S2 precedence, not by S3),
  then stable deterministic order of recognition.

## 5. Knowledge retrieval (S4)

- Input: track domains + query keywords. Index:
  data/knowledge-index-v1.json (sha-verified entries). Content source:
  repository docs listed in the index, read as data, with verbatim spans.
- Output records: topic/domain, claim (verbatim span), source reference,
  authority (mapped from index class), freshness (from index), evidence and
  provenance IDs, gap state.
- Source types: frozen structured rule (rules registry), project research
  evidence (index docs), gap/unknown (GAP_REGISTER - uncertainty only, never
  positive evidence), stale/revalidation required (freshness_class STALE or
  NEEDS_REVALIDATION - never sole authority).
- HISTORICAL_RESEARCH-class content is never sole route authority.

## 6. Local discovery (S5)

- Adapter wraps run_discovery(protocol, input, fixtures=..., mode="replay")
  with the frozen replay fixture manifest. One adapter, one pinned target
  (frozen V1 runtime); no runtime internals copied.
- Trigger: only when a track needs local service information AND a
  municipality is present in location_context (schema-supported). Trigger
  reason recorded as DISCOVERY_TRIGGER_REASON. Absent municipality ->
  NOT_APPLICABLE, no fetch, no discovery failure.
- Failure -> ROUTE_UNVERIFIED + DISCOVERY_INCOMPLETE + ERROR_STATE
  provenance (FC-03: discovery failure never becomes a negative existence
  claim).
- Replay fixture universe: the frozen 17-municipality manifest. No new
  municipalities are introduced.

## 7. Route reasoning (S6)

RouteCandidate carries five separate claim dimensions (authorization section
19): SERVICE_EXISTS, AGE_ELIGIBLE, SCENARIO_RELEVANT, ACCESS_VERIFIED,
CONTACT_VERIFIED. Each dimension is a claim with evidence/provenance refs or
an explicit unresolved state. Downgrades only: a route cannot become
FULLY_VERIFIED unless every required dimension is evidence-backed.

## 8. Evidence aggregation (S7)

Canonical wiring: claim -> evidence IDs -> provenance IDs. Claims without
evidence keep weaker epistemic states. Two authoritative sources in conflict
-> conflict record + SOURCE_CONFLICT state representation (existing enums
only: the conflicting claim stays UNVERIFIED with a failure/conflict record).

## 9. Epistemic collapse (S8)

Frozen doctrine from epistemic-state-contract.md: per-route states from the
five claim dimensions (worst-required-dimension rule); top-level state =
min over tracks (FULLY_VERIFIED > ACCESS_PARTIAL > EXISTENCE_ONLY >
UNVERIFIED). S4 may set at most EXISTENCE_ONLY. S6 downgrades only. No
upgrades beyond mechanical justification.

## 10. Output

sut-output/v1 unchanged. answer is a structured Phase-2 placeholder
(Norwegian, explicitly stating rendering is not implemented, honest
uncertainty list) - authorized by Phase 2 spec section 27. The provenance
span requirement for measurement lanes is a Phase 3 concern; Phase 2
placeholders never assert routes beyond what S6/S7 verified.

## 11. Harness integration

Phase 1 sut_runner/run.py hard-imports sut.pipeline.run_with_trace and
Phase 1 sources are immutable, so Phase 2 ships its own runner in the
Phase 2 lineage: evaluation/full-sut-implementation-phase2/sut_runner/
reusing the Phase 1 loader verbatim (imported, not copied) plus a Phase 2
execute path that dispatches to sut.phase2.pipeline.run_with_trace (same
signature). The runner CLI, gold-stripping, one-shot execution, and
prediction freeze semantics are identical. The extended loader supports
optional location_context passthrough from cases that carry it (schema-valid
per sut-input/v1); corpus cases without location stay unchanged.

## 12. Testing

TDD RED -> GREEN per component: safety precedence, track decomposition,
knowledge retrieval, discovery trigger, discovery failure, route
construction, access partial, provenance, epistemic collapse, source
conflict. Phase 1 suite must still pass against the snapshot (regressions
count: 0). Security guards re-run at the adapter boundary
(SSRF/private IP/redirect/size/timeout/malformed URL/path injection) using
the frozen runtime/discovery/security.py; prompt-injection-as-data test on
the knowledge/discovery data layer.

## 13. Fixtures

48 dev fixtures (burned/dev only): 8 safety, 10 single-track, 10
multi-track, 8 discovery-required, 4 discovery-failure, 4
conflict/incomplete, 4 eligibility-partial. Discovery fixtures use the
frozen 17-municipality replay universe only.
