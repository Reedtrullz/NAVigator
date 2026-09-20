# RC-10 Postmortem (Evidence Attachment, Wave 2)

## Status: PARTIALLY_EFFECTIVE

## Mechanical state
- 673/673 claims carry provenance entries (structural gate PASS).
- 20/20 structured-route cases have provenance (gate PASS).
- Evidence completeness criterion: 0.0 count 38 -> 23; 1.0 count 82 -> 97; no regressions in this dimension.

## PROVENANCE_PRESENT vs PROVENANCE_SEMANTICALLY_SUPPORTS_ASSERTION
- 100 percent claim provenance coverage coexists with 23 criteria still at evidence 0.0 and 108 route FAILs.
- Label->evidence mapping for structured routes is unresolvable 20/20 (R-code keyed, labels are fragments), so semantic support of a route target is not demonstrated by provenance presence.
- Provenance-linked (claim text actually bound to a source) is 59.0 percent, up from 47.8 percent, but this measures linkage, not entailment.

## Verdict
Evidence attachment is structurally improved but semantically incomplete. Evidence repair should be deferred until route/claim selection is fixed: with 89 R0 cases and fragment labels, there is no correct target for evidence to support yet. RC-10 remains open in the sense that semantic support (not just presence) must become measurable after route propositions exist.
