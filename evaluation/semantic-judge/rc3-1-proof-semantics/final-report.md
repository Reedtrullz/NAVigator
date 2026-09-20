# RC3.1 Proof-Semantics Repair - Final Report

Task ID: NAV-EXPLORE-RC3_1-PROOF-SEMANTICS-REPAIR
Date: 2026-09-05
Subagents used: 0
Readiness: **RC3_1_PROOF_NOT_READY**

## 1. What happened this session

The session-4 engine (rc3_1_engine/engine.py) had never been executed and did
not compile: its write step had eaten backslash escapes (line continuations
became orphaned + operators, digit classes lost their backslashes, word
boundaries became literal backspace characters). proposition.py and
decomposition.py were intact and all 21 deterministic probes still passed
because they exercise those two modules, not the engine regexes.

The engine was rewritten once with the same frozen rule design, using a
backslash-free regex style ([0-9] classes, explicit lookaround boundaries) so
this class of corruption cannot recur in this file. All 21 probes pass; both
smoke cases hit expected verdicts.

## 2. First train run (pre-fix baseline)

- Relation accuracy: 96/124 = 77.42%
- Stability: 100% (double run identical)
- Compound count exact: 42/43 = 97.7% (gate >= 97% PASS)
- Boundary exact: 37/43 (matcher artifact; see section 4)
- Unsound auto atoms: 61; R17-negation-flip dominated the error mass

## 3. Root causes found (generalized, no case IDs)

1. Clause-level negation flip ignored negation position and multi-occurrence
   evidence (a positive med-clause next to an ikke-clause fired a flip).
   Fixed: negation must precede the term within a 4-token window in the
   aligned clause (_neg_statuses).
2. R15 universal-vs-discretionary treated "etter" and "minimum" in evidence as
   discretionary markers. Fixed: narrower marker set.
3. R18 double-negation support aligned on any negation anywhere. Fixed:
   shared token must be negation-aligned on both sides.
4. R23 shared-number support fired on any intersection. Fixed: full coverage
   of claim numbers required.
5. qualifier_pairs fired on arithmetic sum lines (1006 + 1286 = 2292). Fixed:
   skip spans containing +.
6. Missing capabilities added: 18+ age notation, arithmetic-sum support
   (evidence addition lines and pair sums), claim-side-restriction-vs-universal
   conflict (R16b), universal-vs-restriction conflict (R15b),
   punctuation-tolerant proper-noun check.

## 4. Post-fix train run (single bounded bugfix pass consumed)

- Relation accuracy: 105/124 = 84.68% (gate >= 95% FAIL)
- Per class: ENTAILS 69/72 (95.8%), CONTRADICTS 20/31 (64.5%),
  PARTIAL 10/14, RBI 3/4, AMBIGUOUS 2/2, UNRELATED 1/1
- Subgroups: condition 93.3%, exception 100%, scope 100%, modality 87.8%,
  negation 55.2% (gate >= 95% FAIL), numeric 90.7%, actor 86.7%
- Compound count exact: 42/43 = 97.7% (PASS)
- Boundary exact: 37/43 under the strict both-sides-exact matcher
  (37/43 also under the previous directional matcher; only the RC31-0064
  sum-claim differs between the two matchers, so this is a gate-metric
  definition issue to freeze, not a decomposition regression)
- Stability: 100%
- Unsound auto atoms: 40 (gate = 0 FAIL); false-ENTAILS 11,
  false-CONTRADICTS 3
- Remaining failure classes: R25-coverage support on scoped/restricted
  evidence, R15/R15b firing on support cases, R23 overlap support, deadline
  sibling-tier leakage, RBI-vs-CONTRADICTS boundary

## 5. Gate decision

Hard train gates not met (relation, negation subgroup, 0 unsound). Per the
task's one-bounded-pass rule, tuning stops here. The validation seal remains
unopened (SHA re-verified below); no validation run; no release candidate; no
new blind set; no routing/reviewer work; RC3G untouched.

## 6. Legacy regressions (read-only, all PASS)

- KB score_baseline.py: 48/48 BESTATT
- Tier-1 run_gate.py: 0 conflicts, 0 invalid proofs, 0 critical auto errors
- Tier-1 operators script: 43/43 PASS
- Operator regression: 23/23 PASS
- RC3-development unit tests: 24 passed
- Quote-aligner: test_polarity_engine ALL PASS; benchmark suites unchanged
  (stability 1.0)
- id_guard: 0 RC1B/RC2B/RC3G/RC31-n hits in rc3_1_engine/ and run_train.py
- Probes: 21/21 pass; train run double-execution deterministic

## 7. Frozen-artifact integrity (re-verified at session end)

- corpus/train-cases.json: fb467faefb7a... (match)
- corpus/validation-cases.json: 3e336d68fc17... (match)
- corpus/validation-answer-key.sealed: 15b13bb7006e... (match, unopened)
- RC3G predictions / official score / cases / seal: all match
  historical-integrity.md SHAs

## 8. Recommended next step

One new R&D task, treating this pass as diagnosis: constrain auto-support to
require scope/modality agreement (extend polarity()-style alignment to R25 and
R23), gate R15b on claim-side existential quantifier, resolve sibling-tier
table leakage via row-index pairing, and freeze the boundary-exact matcher
definition before the next run. Do not resume from this task in-place.
