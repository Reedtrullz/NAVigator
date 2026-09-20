# RC3 Architecture Repair (NAV-EXPLORE-RC3-ARCHITECTURE-REPAIR)

Repairs the generalized architecture failures exposed by the V4 blind run.
RC2 history is immutable: RC2_NOT_CERTIFIED stands permanently.

Five workstreams (spec 5):
A. Proof-bound engine unsoundness (negation/deontic after aligned span)
B. Reviewer/fusion authority (confidence mixer -> monotonic arbitration)
C. Review vs abstain collapse (explicit ABSTAIN_INSUFFICIENT runtime route)
D. Compound decomposition (canonical, claim-logical, before evidence judgment)
E. Scorer display bug (analytics-only fix)

Phases: A then B then C, one implementation pass each (plus one bounded
bugfix pass max), stop gates between phases. No new blind set in this task.
V4 is BURNED_DEVELOPMENT_ONLY: forensics and post-freeze shadow only.

Layout:
- rc3_engine/   repaired components (decomposition, clause-context proof
  validation, proof states, arbitration, routing, abstain)
- tests/        regression suites (negation/deontic, clause scope,
 decomposition, aggregation, arbitration, routing, schema, id guard)
- reports and contracts per the deliverables list in final-report.md

## Outcome

Phase A PASS (proof-bound engine: 0 unsound/invalid accepted proofs,
11/11 negation/deontic regressions). Phase B PASS (decomposition gates,
66-case suite, 100% stability). Phase C: routing gates PASS
(auto precision 1.0, necessary-review recall 1.0, abstain recall 1.0,
macro F1 1.0, 0 overturning reviews) but semantic/proof/product
development gates FAIL on the RC2-tuned sanity corpus; stopped per
spec 48/49. READINESS: RC3_NOT_READY. No release candidate frozen.
Burned V4 shadow was run once, clearly labeled RC3_BURNED_V4_SHADOW_ONLY,
as a diagnostic only; nothing was tuned after it.

Start with final-report.md (77-item SLUTTRAPPORT).
