# Operator regression suite (spec 40)

Permanent regression corpus for the 5 Tier-1 SAFE_FOR_AUTO_PROOF operators.
Run with: python3 run_regression.py (from this directory).

Case classes: one valid positive per operator, invalid precondition,
scope mismatch, time mismatch, ambiguity, cross-operator conflict,
known unsafe near-misses (N-R1 staff-negation binding, ENT-C absence
is not contradiction, MP-015A-style date-of-event vs threshold).

Frozen contract context: dual labels live in ../evaluation-contract/,
operator specs in ../tier1-proof/tier1-operator-spec.md. No case IDs
from live benchmarks appear in runtime code (id_guard scope unchanged).
