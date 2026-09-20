# Repair Priority (Post-Wave-1 Residuals)

Read-only triage. Order = safety impact first, then breadth, root-cause confidence, isolation, regression risk.

| Rank | Candidate | Families hit | Criterion impact | Safety impact | Confidence | Isolation | Risk |
|---|---|---|---|---|---|---|---|
| 1 | RC-08 retrieval scoping | PW1-R4 (+ feeds R1, R2, R5 sub 2) | 6 forbidden + 75 claims + 2 routes + 104 answers + 15 evidence | Medium (stale cross-domain content is a safety-information hazard) | MEDIUM (stage), HIGH (mechanism) | Upstream, single mechanism area | MEDIUM |
| 2 | RC-10 evidence attachment | PW1-R5 sub 1, PW1-R6 | 23 + 3 criteria | Medium (provenance transparency) | HIGH | Very isolated | LOW |
| 3 | RC-11 safety vocabulary | PW1-R3 | 19 criteria | High direction: fixes over-triage noise while preserving under-triage = 0 | HIGH | Isolated classifier | MEDIUM |
| 4 | RC-07 route-target selection | PW1-R1 | 108 criteria | Medium (routing correctness) | HIGH (failure), mechanism hypothesis | Depends on RC-08 | MEDIUM-HIGH |
| 5 | RC-09 premature-absence guard (DEFERRED) | PW1-R2 | 69 criteria | High if wrong; deferred to avoid safety-direction risk | Mechanism proven; fix boundary unknown | Downstream shadow of R1/R4 | HIGH now, LOW later |
| 6 | RC-12 uncertainty wording (DEFERRED) | PW1-R7 | 36 criteria | Low | MEDIUM | Downstream shadow of R1 | LOW |

## Notes

- RC-11 ranks above RC-07 only because it is independently executable and safety-direction-relevant; breadth-wise RC-07 is the largest single mechanism (108 criteria).
- No priority here optimizes the burned Wave-1 score; each candidate names a product mechanism and its observable defect class.
- ROUT-042 (forbidden residual) is LABEL_SENSITIVITY_KNOWN and excluded from candidate sizing; see forbidden-claim-analysis.md.
- All runtime fixes must remain case-ID-free; any candidate justifiable only as "make case X pass" would be flagged OVERFIT_RISK and dropped. None currently is.
