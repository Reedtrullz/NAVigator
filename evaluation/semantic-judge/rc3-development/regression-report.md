# Regression Report (spec 50)

All suites re-run after the final bounded bugfix pass
(`requires_human_review` downgrade now requires grounded reviewer
spans; sufficiency tokens >= 3 chars).

| Suite | Result | Status |
|---|---|---|
| RC3 negation/deontic regression | 11/11 | PASS |
| RC3 decomposition suite | 66 cases, 63 count-exact (95.45%) | PASS (gate >= 95%) |
| RC3 arbitration tests | 6/6 | PASS |
| RC3 routing tests | 4/4 | PASS |
| RC3 reviewer tests | 5/5 | PASS |
| RC3 review-vs-abstain suite | 16/16 | PASS |
| RC3 analytics display regression | 2/2 | PASS |
| RC3 id guard | 0 runtime hits | PASS |
| RC2 frozen engine regression | 37/37 | PASS |
| Tier-1 operators | 43/43 | PASS |
| Operator regression | 23/23 | PASS |
| Quote-aligner regression | ALL PASS (incl. injection, determinism) | PASS |
| KB baseline | 48/48 BESTATT | PASS |
| RC2 hash verification (hashes.txt) | all OK | PASS |
| Determinism (225 cases x 5 runs) | identical | PASS |
| Runtime robustness (160 shadow rows + 45 dev rows) | 0 failures | PASS |
| qa_check.sh | not found in this tree | N/A |

Safety canaries: no regressions (RC2 37/37 includes the
numeric/temporal canaries; Tier-1 and aligner suites all green).

## Runtime stability (spec 46/40)

evaluate_dev.py: 45/45 registered outcomes, 0 unhandled exceptions.
Burned V4 shadow: 160/160 registered outcomes, 0 runtime failures.
