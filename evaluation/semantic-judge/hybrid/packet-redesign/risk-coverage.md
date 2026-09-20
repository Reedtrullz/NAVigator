# Risk-coverage after packet-v2.1 (gate subset only)

The Iteration-A gate failed (novel-40 not improved), so per spec 43 the
full suite was not run. Risk-coverage is therefore reported on the gate
subset (96 claims: minimal-pairs, supplement, novel-40, ent) and compared
with Iteration B on the same subset.

| Metric | Iteration B (subset) | packet-v2.1 no_s0 |
|---|---|---|
| decided | 90 | 92 |
| selective accuracy | 0.8333 | 0.8043 |
| REVIEW_REQUIRED | 6 | 4 |
| auto SUPPORTED FP | 0 | 0 |
| auto CONTRADICTED FP | 0 | 0 |
| fidelity failures | 0 | 0 |

## Reading

* Coverage (auto+review decided rate) is unchanged or marginally up;
  RR fell 6 -> 4 on the subset and 5 -> 1 on novel-40.
* Safety did not degrade: zero auto-path FPs in every variant, zero
  fidelity failures, injection probe still locked (CAL086 stays
  INSUFFICIENT/REVIEW_REQUIRED, never SUPPORTED).
* Accuracy did not improve: the support-recall gains the redesign was
  built for did not materialize, because the residual SUPPORTED->INSUFFICIENT
  errors are reviewer-reasoning failures (oracle packets only reach
  7/45 on the B error set; 0/8 on novel-40 errors).
* S0 include scored higher on the subset (0.8427) but did not fix the
  B error cases either (0/45); its higher subset accuracy comes from
  fixed rows unrelated to the audit taxonomy, and it broke ENT-D into
  human-review. No mode is a clear win; the mode matrix is in
  final-report.md.

Conclusion: packet redesign is NOT the binding constraint at this stage.
The risk-coverage frontier is reviewer-limited, and moving it requires
either a doctrine/model change (out of scope) or accepting a higher
REVIEW rate.
