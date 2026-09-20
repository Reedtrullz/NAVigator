# Analysis (structured-proof probe)

## Headline

The frozen v1.1 reviewer is already near the ceiling of its own doctrine.
On the 24-case probe set its baseline doctrine accuracy is 22/24 (91.7%),
while its benchmark accuracy is 5/24 (20.8%). Of the 46 audited cases,
33 (71.7%) have benchmark expected-labels that diverge from the
doctrine-consistent verdict. The oracle "errors" are therefore dominated
by a semantic-target mismatch, not by reviewer reasoning failures.

## Metrics

| Metric | Value |
|---|---|
| Audit coverage | 45/45 oracle cases + ENT-D canary |
| Categories | A=6, B=17, C=12, D=3, E=6, F=2 |
| Probe set (A/B/F) | 24 cases (5 A, 17 B, 2 F) |
| Negative controls (C/D/E) | 21 |
| Baseline probe benchmark acc | 5/24 = 20.8% |
| Baseline probe doctrine acc | 22/24 = 91.7% |
| Structured-proof benchmark acc | 3/24 = 12.5% |
| Structured-proof doctrine acc | 14/24 = 58.3% |
| Direct-proof accuracy (bench/doc) | 2/5 / 2/5 |
| Bounded-inference accuracy (bench/doc) | 1/17 / 12/17 |
| NO_OPERATOR rate (probe) | 15/24 |
| Control refusal accuracy | 16/21 = 76.2% |
| Control doctrine-consistency | 16/21 |
| Genuine auto-verdict overreach on controls | 1 (D20-L5 PARTIAL) |
| Safe REVIEW_REQUIRED on controls | 2 (LOC-10, ENT-A) |
| Proof validation pass-rate (probe) | 20/24 |
| Hallucinated premises in ACCEPTED proofs | 0 |
| Invalid inference rate (probe) | 4/24 = 16.7% |
| Operator stability | 5/5 claims x 3 consistent |
| Premise-selection stability | 5/5 |
| Verdict stability | 5/5 |
| Benchmark-vs-doctrine disagreements | 33/46 = 71.7% |
| POTENTIAL_BENCHMARK_LABEL_ISSUE | 8 |
| Luna calls | 63 (24 probe + 21 controls + 15 stability + 3 setup) |
| Tokens (estimated, 809p/288c avg) | ~51k prompt / ~18k completion |
| MODEL | openai/gpt-5.6-luna, temp 0, max_tokens 300 |

## Interpretation

1. The structured-proof variant made things WORSE, not better: the model
   responds to the proof burden with NO_OPERATOR/INSUFFICIENT on 15/24
   probe cases, including trivial equivalence cases (N-L4, N-C5, ACT-19).
   The refusal is perfectly stable (5/5 x 3), so this is a conservative
   policy, not noise.
2. Baseline v1.1 misses only 2 doctrine targets: N-L4 (F: flagged a
   paraphrase-level entailment for review) and N-C5 (B: direkte = uten
   henvisning same-clause implication). Both are small bounded-operator
   cases, not open-ended reasoning.
3. Contradiction overreach is contained: zero accepted SUPPORTED or
   CONTRADICTED without a validator-passing proof in the probe run; the
   only auto-verdict overreach on controls was D20-L5 (PARTIAL via
   DIRECT_ASSERTION on a locality gap). The EXHAUSTIVE_SET_EXCLUSION
   precondition correctly blocked all closed-world slides (CAL029,
   CAL030, N-R3, CI-046, CI-059).
4. The two false-CONTRA clusters from the oracle baseline (CI-*, E cases)
   are label-vs-doctrine disagreements: the benchmark demands CONTRA
   where proof doctrine (correctly) yields INSUFFICIENT, or vice versa
   (CI-040/CI-061/CI-065/LOC-10/HOL020).

## Decision tree (spec 30)

Selected: CURRENT_PROOF_DOCTRINE_IS_TOO_STRICT (B).

Rationale: nearly half of the oracle errors (21/45) are C/D/E - the
evidence does not permit the benchmark verdict under any reviewer
reasoning - and 33/46 benchmark labels diverge from doctrine-consistent
verdicts. Model R&D cannot close a target-definition gap.

Rejected alternatives:
- A (reasoning viable): bounded-inference benchmark accuracy is 1/17;
  a proof-graph layer is not currently viable as specified.
- C (evidence insufficient): only 3/45 cases are genuinely D.
- D (reviewer reasoning ceiling): baseline doctrine accuracy is 91.7%;
  the reviewer does NOT fail significantly on doctrine-provable cases.

## Secondary contributing causes

- Bounded-operator gap: 17 B cases need one small operator layer
  (TRANSITIVE_EQUIVALENCE, RULE_PLUS_CONDITION, NUMERIC_CONFLICT with
  threshold comparison, SAME_PREDICATE_OPPOSITE_POLARITY with
  distributional reading). This is evidence-layer work, next stage.
- Structured-proof format as tested is over-conservative; if retried,
  the operator descriptions need worked examples per operator.
- Validator strictness converted 2 would-be-correct PARTIALs into
  REVIEW_REQUIRED (CAL048/CAL050 EXPLICIT_NEGATION precondition too
  narrow for multi-atom proofs).

## What NOT to do next (spec 31, 32, 33, 34)

- Do not tune the reviewer prompt against benchmark labels.
- Do not build packet R&D, holdout-v3, blind recert, or live dialog.
- Do not treat EXHAUSTIVE_SET_EXCLUSION as allowed without explicit
  markers; that re-opens the v0.3 false-CONTRA wound.
- Do not re-run the structured variant with more iterations (max-1 rule).

## Recommended next architectural step (44, not implemented)

Redefine the evaluation target first: split benchmark scoring into
"proof-doctrine score" (current) and "semantic intent score" (bounded-
inference-permitting), then implement the small bounded-operator layer
listed above in the deterministic layer, not in the reviewer prompt.
