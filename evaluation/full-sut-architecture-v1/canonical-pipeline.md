# Canonical Pipeline

End-to-end answer/decision pipeline for the full SUT, adapted to this repo.
Stage order is normative; each stage reads only its declared inputs and the
DecisionContext (decision-context.schema.json).

    USER INPUT
       |
       v
    S1 input normalization
       |
       v
    S2 safety / urgency triage
       |
       v
    S3 problem decomposition
       |
       v
    S4 knowledge + legal retrieval
       |
       v
    S5 local discovery (conditional)
       |
       v
    S6 route / eligibility / access reasoning
       |
       v
    S7 evidence aggregation
       |
       v
    S8 epistemic-state assignment
       |
       v
    S9 answer planning
       |
       v
    S10 user-facing answer rendering
       |
       v
    S11 structured SUT evaluation output

## S1 Input normalization

- Input: sut-input/v1 object (sut-boundary.md).
- Behavior: normalize whitespace and casing of the query; validate profile.age
  as integer 0-120 when present; validate timestamp_context.executed_at as ISO
  8601 UTC; pass location_context through unchanged (municipality names are
  matched later, never guessed).
- Failure: malformed input -> terminal EXECUTION_FAILED with
  presented_as_complete=false; nothing downstream runs.
- Determinism: fully deterministic.

## S2 Safety / urgency triage (first-class, ADR-002)

- Input: normalized query + profile.
- Behavior: deterministic keyword/pattern triage against the validated safety
  vocabulary already established in the dev corpus and knowledge artifacts
  (57-nodhjelp-og-akutte-situasjoner.md, 42-vold-trusler-og-sikkerhet.md).
  Emits safety.priority in {ACUTE_RISK_NOW, URGENT_NOT_ACUTE, NOT_ACUTE} plus
  matched signals. ACUTE_RISK_NOW sets suppressed_routing=true: S4-S6 run only
  to source the emergency instruction; ordinary route recommendation is
  suppressed and the emergency route (113 / 116 123 / 116 117 / legevakt per
  corpus gold semantics) becomes the primary output.
- Signals: explicit self-harm/suicide ideation terms, acute danger terms,
  crisis vocabulary. The triage rule set is a frozen data file, not inline
  code, so evaluator review can audit it.
- Failure: triage itself cannot fail open. If the rule file is missing or
  invalid -> terminal failure (fail-closed-contract.md FC-01).
- Determinism: fully deterministic. The LLM is never the sole authority for
  emergency escalation (ADR-006); triage may later be assisted by an LLM, but
  the deterministic layer alone must already catch the corpus safety cases.

## S3 Problem decomposition

- Input: normalized query + safety state.
- Behavior: split multi-domain requests into parallel problem tracks
  (mental_health, housing, financial_support, child_safety, education,
  employment, ...). Each track carries the sub-utterance, the profile slice,
  and its own downstream verdict slots. Conjunction splitting is conservative:
  one domain if unsure, multiple only on clear signals (og / i tillegg /
  distinct need nouns). Safety priority propagates as a global cap on all
  tracks.
- Failure: decomposition can always fall back to a single track (partial
  success, RECOVERABLE); a decomposition failure never blocks answering the
  dominant domain.
- Determinism: deterministic in Phase 1-3 implementation; an LLM decomposer
  may replace it later under ADR-006 constraints (LLM may propose tracks, the
  deterministic merger keeps safety cap and track stability).

## S4 Knowledge + legal retrieval

- Input: per-track sub-utterance + profile.
- Behavior: query the knowledge layer (knowledge-layer-interface.md) over the
  existing markdown artifacts: stable legal/factual docs, decision-support
  docs (26, 28b/c, 45), and source documentation. Returns per-track evidence
  items: supporting spans with artifact path + section, authority level,
  freshness class. Hard legal deadlines/eligibility come from the structured
  rules registry (15-regler/rules-v1.json), never from LLM recall.
- Failure: artifact unreadable/missing -> that track gets NO_KNOWLEDGE_EVIDENCE
  (recoverable); the track may still proceed to discovery if it is a
  discovery-type need.
- Determinism: retrieval is deterministic (regex/keyword scoring over frozen
  artifacts); span extraction is verbatim.

## S5 Local discovery (conditional)

- Input: tracks whose need type requires local services (municipal psykisk
  helse, HFU, family centers) + location_context + age.
- Behavior: call the frozen discovery runtime adapter
  (local-discovery-interface.md) over runtime/discovery (V1 frozen) with the
  V2.4 candidate semantics. Returns structured discovery result with
  provenance graph, route_state, execution_status. The SUT never reimplements
  discovery logic and never treats discovery failure as non-existence.
- Failure: mapping to fail-closed states per fail-closed-contract.md FC-03.
- Determinism: discovery is bounded and protocol-frozen; replay mode is
  deterministic, live mode is recorded per execution.

## S6 Route / eligibility / access reasoning

- Input: tracks + knowledge evidence + discovery results + profile.
- Behavior: per track, evaluate candidate service routes: age gates, referral
  requirements, access conditions, using the structured rules registry first
  (deterministic eligibility), knowledge spans second, discovery route states
  third. Emits candidate routes with per-route epistemic_state and
  provenance_ids. Under safety suppression (S2), emergency routes only.
- Failure: no candidate route for a track -> no_route_asserted=true at track
  level (not a fabricated route); explicit uncertainty entry required when
  gold-known uncertainty dimensions exist (age under threshold, capacity
  unknown).
- Determinism: fully deterministic rules; ambiguity resolves to
  uncertainty_expressed entries, never to confident fabrication.

## S7 Evidence aggregation

- Input: all track evidence + discovery results.
- Behavior: merge evidence into the flat evidence map keyed by
  required-evidence-field vocabulary (safety_priority, source_url,
  aldersgrunnlag, kontaktvei, accessed_at, ...), attach provenance_ids, drop
  duplicates, mark conflicts (two sources disagree) explicitly.
- Failure: aggregation cannot fail; worst case it passes through empty maps
  with failure entries from earlier stages.
- Determinism: fully deterministic.

## S8 Epistemic-state assignment

- Input: aggregated evidence + route states.
- Behavior: assign per-route and top-level epistemic_state using the frozen
  precedence in epistemic-state-contract.md. Only stages S4/S5/S6 may propose
  states; S8 collapses them deterministically.
- Failure: cannot fail; defaults to UNVERIFIED on any unresolvable input.
- Determinism: fully deterministic.

## S9 Answer planning

- Input: DecisionContext through S8.
- Behavior: order content blocks: safety instruction first (if any), then
  primary track routes, then secondary tracks, then uncertainty statements,
  then provenance list. Decide presented_as_complete (true only if no stage
  failure affects the answer and all tracks resolved to at least EXISTENCE_ONLY
  or better) and no_route_asserted.
- Failure: cannot fail; degrades to minimal honest answer ("kunne ikke
  verifisere...") when inputs are empty.
- Determinism: fully deterministic planner; text rendering may use templates.

## S10 Answer rendering

- Input: answer plan.
- Behavior: render user-facing Norwegian text from frozen templates + span
  quotes. Quotes must be verbatim from evidence spans so that sut_output
  substring checks in the measurement lanes pass.
- Failure: template missing -> fail-closed to plain span listing
  (RECOVERABLE).
- Determinism: deterministic given the plan. If an LLM polishes prose later,
  ADR-006 requires: same facts, no new claims, span-preserving, and the
  deterministic draft is the fallback on any violation.

## S11 Structured output emission

- Input: DecisionContext through S10.
- Behavior: emit sut-output/v1 (sut-output.schema.json), including the raw
  answer object fields the scorer consumes. execution_status: SUCCESS only if
  no terminal failures; DISCOVERY_INCOMPLETE / EXECUTION_FAILED map per
  fail-closed-contract.md.
- Failure: schema validation failure of our own output is a bug -> recorded as
  terminal failure with the raw context dumped to the harness error store.
- Determinism: fully deterministic.

## Priority order across tracks

ACUTE safety > urgent safety > child safety > active legal deadlines >
eligible-route resolution > general information. The order is frozen here;
track ranking in S9 uses it.
