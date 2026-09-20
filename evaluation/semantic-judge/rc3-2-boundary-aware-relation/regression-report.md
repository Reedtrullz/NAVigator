# RC3.2 Regression Report

Engine after task: sha256 16d4fdbf34afe1ca460c6ea2c43b2937dc1cc4c7ace21c4da6324520a28b2f20
Boundary after task: sha256 9200aa9033bb25eaa63dcb23552f814b0e079accff86b97c48c3ef026343fc1e

## Legacy battery (spec section 41)

| Suite | Result |
|---|---|
| RC2 regression | 37/37 pass |
| Tier-1 gate | clean (0 conflicts, 0 new invalid proofs, 0 critical auto errors) |
| Tier-1 operators | 43/43 pass |
| Operator regression | 23/23 pass |
| RC3 dev pytest | 24/24 pass |
| Evaluator regression | TP=24 TN=96 FP=0 FN=0, acc 1.00 |
| KB baseline | 48/48 BESTATT |
| Engine probes | ALL PASS |
| Decomposition | 44/44 pass |
| Frozen boundary suite | FALSE_AUTO 0, precision 1.0, recall 0.973, unsound eligible 0 |
| id_guard | 0 hits for RC1B/RC2B/RC3G in engine runtime |
| Determinism | two full harness runs byte-identical |
| Gate equivalence | 0/677 gate diffs, 0 projection mismatches |
| Sealed validation SHA | 15b13bb7... unchanged; never opened |
| Runtime robustness | py_compile OK on both edited modules; no exceptions across 152-case + 80-case + legacy runs |

No safety regressions in the legacy battery.

## Quote-aligner drift (spec section 42)

The historical quote-aligner mismatches (4 Sep-2 mismatches, 2
date-window drift mismatches) are documented in earlier task reports.
The quote-aligner standalone engine has NO import path into the RC3.2
runtime (verified: no quote_aligner import in rc3_1_engine/ or this
task directory). Per spec, they are NOT counted as RC3.2 failures and
were NOT patched in this task.

## Incident: accidental overwrite of a historical artifact

While re-running the frozen boundary suite for verification, the
boundary harness was invoked with its default output path, which
overwrote rc3-1-support-boundary/baseline-results.json (the
pre-implementation baseline from the earlier boundary task). The
original bytes are not recoverable. The file was restored as an
explicitly labeled HEADLINE_ONLY reconstruction carrying the documented
facts (FALSE_AUTO=27, precision 0.5345, from that task README) and a
full incident description. The incident was a run-path mistake, not a
silent mutation: no manifest-listed artifact was affected (verified
against candidate-boundary/hashes.txt: all files still match their
frozen SHAs except the two engine modules this task intentionally
changed).
