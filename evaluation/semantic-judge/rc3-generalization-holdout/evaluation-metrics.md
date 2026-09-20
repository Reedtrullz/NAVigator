# Preregistered Evaluation Metrics and Gates

Frozen before any holdout scoring (spec 39/40/42). Authority chain:
proof-soundness-contract-v2.{md,json} defines M1-M5; this file
preregisters the pass/fail gates for the future G1/G2 scoring.

## Proof safety (each must be exactly 0)
- M1 structural invalid accepted proofs = 0
- M2 ungrounded accepted proofs = 0
- M3 semantically unsound accepted proofs = 0 (atom granularity)
- M4 proof-safe unsound autos = 0 (case granularity)

## Auto and routing
- Combined auto precision (M4/M5-based) >= 99%
- Auto coverage >= 20% (anti-trivial-review floor; no architecture
  contract overrides this)
- Necessary-review recall >= 95%
- Unnecessary-review rate <= 15%
- Abstain recall >= 90%
- Review-vs-abstain macro F1 >= 90%
- Auto / review / abstain coverage reported separately (no bucket may
  hide failure by absorbing everything)

## Accuracy
- Semantic >= 90%
- Proof-safe >= 95%
- Product >= 95%

## Compound
- Compound atom semantic >= 90%
- Compound product >= 90%
- Atom count exact, atom semantic exact, missing atom rate, extra atom
  rate, top-level aggregation correctness: all reported separately

## Runtime
- Unhandled exceptions = 0; 100% registered outcomes

## Construction-stage results (already achieved, for provenance)
Semantic agreement 91.82%, proof-safe 91.19%, product 90.57%,
atom count 100%, adjudication rate 11.95% (0 unresolved), fidelity
0 mismatches, novelty 0 rejects, CORE 159, all quotas pass. These are
construction gates; runtime gates remain open until G1/G2.

No threshold in this file was tuned on V4 or on snapshot behavior
(spec 43); V4 is provenance for why the metric layers exist.
