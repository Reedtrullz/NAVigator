# INTERFACE_GAP-001 Adjudication

Owner decision (Phase 2 authorization, section 0):

> TRIAGE_FAILED remains an INTERNAL fail-closed state. It is NOT added to
> sut-output/v1. When internal triage ends TRIAGE_FAILED, ordinary
> routing must not continue, output uses the existing canonical terminal or
> failure representation, failure details preserve the triage-failure root
> cause, and no verified safety claim is produced. No schema change.

## Existing schema can represent this without semantic loss

The frozen sut-output/v1 schema already carries everything needed, and
Phase 1 runtime/sut/pipeline.py (S11, output_emission) already implements
the required mapping. Phase 2 preserves this mapping verbatim:

1. Internal ctx["safety"]["priority"] == "TRIAGE_FAILED" never reaches the
   output enum. The output safety.priority field takes the worst-case
   canonical value ACUTE_RISK_NOW as a fail-closed placeholder.
2. The accompanying failure record (stage safety_triage, state TERMINAL)
   carries the root cause: the safety rules file was missing, corrupt, or
   produced an invalid state (FC-01), or triage evaluation itself failed.
3. execution_status becomes EXECUTION_FAILED and presented_as_complete
   stays false; no route or verified claim is emitted
   (no_route_asserted: true).
4. answer is the canonical refusal text, never a user-facing claim.

## Phase 2 behavior

Phase 2 S2 performs real triage evaluation, but the same mapping applies
whenever triage cannot produce a verified verdict: rules file unreadable,
invalid structure, evaluation crash, or any state outside the canonical
ACUTE_RISK_NOW / URGENT_NOT_ACUTE / NOT_ACUTE set. Ordinary routing is
suppressed, no verified safety claim is produced, and the failure record
preserves the triage-failure root cause.

No stop condition applies: the frozen output schema represents this
fail-closed state without semantic loss and without schema change.
