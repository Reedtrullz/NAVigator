# packet-redesign (SEMANTIC-JUDGE-EVIDENCE-PACKET-REDESIGN)

Evidence-packet redesign on top of hybrid Iteration B (frozen). Reviewer
doctrine v1.1 unchanged except syntactic schema addendum (prompt SHA
7377d10307e2fb7d, packet-v2.1).

## Outcome

Iteration-A gate FAILED (novel-40 76.9% vs required > 77.1%; correct
count improved 27 -> 30 and RR 5 -> 1, but the rate did not clear the
gate). Per spec 43: stopped before Iteration B and the full suite.
Oracle packets reach only 7/45 on the B error set (0/8 novel-40
errors), so the ceiling is reviewer reasoning / evidence availability,
not packet routing.

## Files

* TASK-LOCK.json - task identity and completion state
* packet-error-audit.md - 45-case taxonomy (S0 distraction, binding,
  retrieval ceiling, contradiction boundary)
* packet-schema.md - packet-v2.1 schema + exact prompt diff
* router-spec.md - automatic router pipeline
* run_packet_eval.py - runner (--s0-mode, --max-spans, --dry-run)
* run_oracle.py - oracle packet experiment (diagnostic only)
* build_audit.py - rebuilds B-error packets (audit-data.json)
* results/iterationA-gate.json - no_s0 max6 gate run (59 calls)
* results/iterationA-s0-include.json / -fallback.json - S0 matrix
* results/size-4.json / size-8.json - packet-size matrix
* results/oracle-packet-results.json - oracle diagnostic
* risk-coverage.md, cost-analysis.md, final-report.md

## Reproduce

    python3 run_packet_eval.py --dry-run
    python3 run_packet_eval.py --sets minimal-pairs,novel-40,ent \
        --s0-mode no_s0 --max-spans 6 --out results/x.json
    python3 run_oracle.py

Regressions verified during task: quote-aligner 0, KB 48/48.
No KB changes, no id_guard violations, no holdout-v3, no blind recert.
