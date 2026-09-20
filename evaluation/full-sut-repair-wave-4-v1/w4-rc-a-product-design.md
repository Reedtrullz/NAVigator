# W4-RC-A Product Design (frozen)

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-4-V1, Phase A only.

## Root causes addressed

- R0 (84/108): prose claims under service headings minted no route
  target although the heading itself is the service identity
  ("## Skolehelsetjenesten"). Fixed generically by a fail-closed
  heading-context rescue: the claim must appear verbatim on exactly one
  line of the referenced source document; the nearest preceding heading
  becomes the candidate after identity gates (digits allowed on this
  path because names like "Helsestasjon 0-5 ar" are legitimate).
  Table rows are excluded from the rescue: they remain exclusively the
  header-identity-gate's domain (W3-RC-A), so scenario/source-ref rows
  can never mint targets through the new path.
- B4 (16): quoted/bold extraction minted non-service labels. Fixed by
  the shared identity gate `_valid_service_name`: sentence-fragment
  signatures (verb/negation starters, trailing punctuation, closed
  subject+verb clause opener list) and unresolved all-caps acronyms
  ("NAV", "URL") are rejected; documented service acronyms (BUP, HABU,
  RPH, DPS, HFU, PPT) stay accepted.
- B5 (23): finalize dropped the structured route object and kept only
  display labels. Fixed by serializing per-route structured objects
  (route_id, service_identity, display_label, track_domain, route_state,
  access_model, self_referral, target_population, scope, evidence_refs,
  provenance_refs, dims) into the additive evidence map
  (`evidence.structured_routes`), which is `additionalProperties: true`
  in the frozen output schema. The public `routes` list stays
  labels-only; no schema file was mutated.
- Evidence binding: discovery routes now bind to the evidence rows of
  their own source URL (`_bind_discovery_evidence`) instead of
  blanket-crediting every E-DISC ref. Documented ceiling: when the
  service record carries no source_url, all refs are bound (fallback).

## Authority / safety invariants

- No gold-aware target selection; extraction is generic and lexical.
- No case IDs or burned-corpus strings in runtime logic.
- Fail-closed: ambiguous claim location, unreadable source, non-identity
  heading, fragment signature or unresolved acronym -> no route target.
- Deterministic override of nothing: all new code paths are pure
  functions over frozen inputs plus the referenced source document.

## Files changed

- runtime/sut/phase2/routes.py (extraction gates, heading rescue,
  evidence binding)
- runtime/sut/phase3/finalize.py (structured_routes serialization)
- runtime/sut/phase3/test_route_binding_wave4.py (new W4 test file)
