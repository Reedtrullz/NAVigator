# RC3.3.1 Regression Report

## Development-60 (post-fix, frozen)

relation 1.0 | macro-F1 1.0 | CONTRADICTS P 1.0 (21/21) | ENTAILS P 1.0 (26/26)
| RBI R 1.0 (13/13) | false_stale 0 | failing_rules {} | temporal 1.0 on 58
| quantity 1.0 on 56 | comparator 1.0 on 11 | law_ref 0 | unsound 0.
All 19 baseline misses repaired. See development-results.json.

## Global-140 burned regression (post-fix, frozen)

relation 1.0 (140/140) | macro-F1 1.0 | ENTAILS P 1.0 | CONTRADICTS P 1.0
(40/40; R33-126 repaired, ancestor baseline 0.9756) | RBI recall 1.0
| quantity identity 1.0 on 68 | false_stale 0 | law_ref 0 | unsound 0
| critical false E/C 0 (proof-safety-audit.json).

## Proof safety audit

dev: 25 ENTAILS atoms (24 grounded; 1 ungrounded is boundary-BLOCKED, 0 accepted
ungrounded), 0 critical false E/C. global: 56 ENTAILS atoms all grounded,
0 critical false E/C. 0 hallucinated / structural-invalid / ungrounded accepted
proofs. case_id_rules_in_runtime = 0.

## Boundary invariance

boundary.py SHA 9200aa90... byte-identical to frozen RC3.2/RC3.3 artifact;
proposition.py byte-identical. Frozen 80-case boundary suite result stands by
input identity: projection diffs 0, false auto support 0, precision 1.0,
recall 0.973, unsound eligible support 0.

## Legacy battery

RC2 regressions 37/37, Tier-1 43/43, operator 23/23, RC3.1 probes ALL PASS,
R31/R32 runners reproduce frozen baselines (0.6277/0.6866 and 0.514/0.4693,
collapse 0.1034) - burned diagnostics, no tuning performed. Sibling SHAs match
frozen provenance. Not-run items and reasons preserved in
results/legacy-regression-report.json.

## Integrity and reliability

id_guard 0 hits | determinism byte-identical | 0 control characters
| sealed SHAs unchanged: fresh-targeted-cases.json 7228cffa...,
micro-validation.sealed f9c9b371..., large sealed 15b13bb7...
| HISTORICAL_FILES_MODIFIED = 0 | runtime failures 0.

## Hidden micro-validation

One execution only, BEFORE freeze (protocol deviation, voided as a section-32
validation): relation 0.8667, C-prec 0.8182, false-stale 2, unsound 1,
quantity 0.8571, temporal 0.9643, comparator 1.0 (3), law-ref 0.
Burned as diagnostics: results/micro-validation-premature-void.json.
No rerun. Status consequence: RC3_3_1_RESIDUAL_REPAIR_NOT_READY.
