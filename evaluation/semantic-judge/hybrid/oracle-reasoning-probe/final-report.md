# Final Report — SEMANTIC-JUDGE-ORACLE-REASONING-PROBE

- Date: 2026-09-02
- Spec: /Users/reidar/.codex/attachments/883165f7-f728-4677-bbf9-bd94c56b9744/pasted-text-1.txt (SLUTTRAPPORT, 44 points)
- Work dir: /Users/reidar/Projectos/NAV Explore/evaluation/semantic-judge/hybrid/oracle-reasoning-probe/
- Model: openai/gpt-5.6-luna via local proxy (http://127.0.0.1:10100/v1/chat/completions), temp 0, max_tokens 300
- Deliverable: analysis only. No packet R&D, no holdout-v3, no blind recertification, no live dialog, no next-step implementation.

1. **Task-lock**: TASK-LOCK.json present with task_id SEMANTIC-JUDGE-ORACLE-REASONING-PROBE, task_family semantic-judge, component oracle-reviewer-reasoning-analysis. All forbidden tasks respected (no packet-routing development, holdout-v3, blind recertification, live dialog, municipal/NAV research, KB tuning, model bakeoff). Status flipped to COMPLETED on 2026-09-02 after deliverables.

2. **Baseline oracle-result**: frozen v1.1 baseline = 7/45 correct, from ../packet-redesign/results/oracle-packet-results.json, preserved verbatim in baseline-results.json with provenance header.

3. **Oracle cases auditet**: 45/45 first-hand re-verified + ENT-D canary = 46 ledger rows (oracle-proof-ledger.json; validator: 0 errors).

4. **DIRECTLY_PROVABLE (A)**: 6 (incl. CAL048, CAL050, HOL026, HOL040 OK-canaries and LOC-20 deontic-implicit canary).

5. **PROVABLE_WITH_BOUNDED_INFERENCE (B)**: 17.

6. **DOCTRINE_BLOCKED (C)**: 12.

7. **EVIDENCE_INSUFFICIENT (D)**: 3 (incl. ENT-A).

8. **EXPECTED_LABEL_QUESTIONABLE (E)**: 6 (CI-040, CI-061, CI-065, LOC-10, HOL020, +1; expected labels diverge from doctrine).

9. **REVIEWER_REASONING_FAILURE (F)**: 2 (N-L4, N-C5 — both small bounded-operator slips).

10. **Novel-40 fordeling**: 5/8 B, 1/8 F, 1/8 C, 1/8 D — error mass is target-definition driven, not reasoning collapse.

11. **ENT-A**: category D. The foreldresamtale premise is genuinely absent from sources; INSUFFICIENT is the correct doctrine verdict.

12. **ENT-D**: baseline CONTRADICTED canary; explicit negation is present in spans. ENT-A vs ENT-D separates missing premise (D) from explicit negation (catchable). Not in the 45-case pool.

13. **Identifiserte inference operators**: all 15 spec operators implemented mechanically in validate_proof.py and exported to inference-operators.json (full list in proof-validator-spec.md). Each has deterministic preconditions; EXHAUSTIVE_SET_EXCLUSION requires an explicit closed-world marker (kun/bare/eneste/alle/...).

14. **Operators faktisk trengt**: direct cases used DIRECT_ASSERTION / EXPLICIT_NEGATION; the 17 B cases need a small bounded layer: TRANSITIVE_EQUIVALENCE, RULE_PLUS_CONDITION, NUMERIC_CONFLICT (threshold comparison), SAME_PREDICATE_OPPOSITE_POLARITY (distributional reading).

15. **Operators forkastet som unsafe**: EXHAUSTIVE_SET_EXCLUSION without explicit markers — correctly blocked closed-world slides on CAL029, CAL030, N-R3, CI-046, CI-059. Conservative preconditions on bounded operators drove NO_OPERATOR refusals on B cases instead of unsafe derivations.

16. **Baseline v1.1 benchmark accuracy på probe-set**: 5/24 = 20.8%.

17. **Baseline doctrine accuracy**: 22/24 = 91.7% (misses only N-L4 and N-C5).

18. **Structured-proof benchmark accuracy**: 3/24 = 12.5%.

19. **Structured-proof doctrine accuracy**: 14/24 = 58.3%; NO_OPERATOR refusals on 15/24.

20. **Direct-proof accuracy**: benchmark 2/5, doctrine 2/5.

21. **Bounded-inference accuracy**: benchmark 1/17, doctrine 12/17.

22. **NO_VALID_DERIVATION accuracy på C/D/E controls**: 16/21 = 76.2% doctrine-consistent refusals (INSUFFICIENT + NO_OPERATOR); 2 safe REVIEW_REQUIRED (LOC-10, ENT-A); 1 genuine overreach (D20-L5, PARTIAL via DIRECT_ASSERTION).

23. **Proof validation pass-rate**: 20/24. Fails: N-C4 (insufficient premise + operator), CAL048 and CAL050 (EXPLICIT_NEGATION precondition too narrow for multi-atom proofs), HOL030 (premise overlap + hallucination flag).

24. **Proof hallucination rate**: 0 hallucinated premises in ACCEPTED proofs (prefix-4 + compound substring matching).

25. **Invalid inference rate**: 4/24 = 16.7% (validator-rejected proofs).

26. **False SUPPORT**: 0 with valid proof, 0 with invalid proof in the probe run.

27. **False CONTRADICTION**: 0 in the probe run; the baseline CI-*/E false-CONTRA clusters are benchmark-label-vs-doctrine disagreements, not probe-run contradictions.

28. **Operator stability**: 5/5 hardest claims x 3 runs consistent.

29. **Premise-selection stability**: 5/5.

30. **Verdict stability**: 5/5 (stable NO_OPERATOR refusals — conservative policy, not noise).

31. **Benchmark-vs-doctrine disagreement**: 33/46 = 71.7%.

32. **POTENTIAL_BENCHMARK_LABEL_ISSUE**: 8 (CI-040, CI-041, CI-061, CI-065, LOC-10, HOL020, CAL086, CAL089). Separate notes: CAL089 injection analysis and LOC-20 modal canary (deontic: lovpaalagt plikt implies kan etablere).

33. **Novel-40 implication**: even in the fresh error subset the reviewer's dominant failure mode is being asked for verdicts the evidence cannot carry under doctrine (B/C mass), with only 1/8 genuine reasoning failure.

34. **ENT-A/D implication**: the reviewer separates explicit negation from absent premises correctly; the canary structure confirms the C/D taxonomy is real, not reviewer noise.

35. **Luna calls**: 63 total (24 probe + 21 controls + 15 stability + 3 setup), all openai/gpt-5.6-luna, temp 0, max_tokens 300. Latencies 2.1-11.8 s.

36. **Token usage**: ~51k prompt / ~18k completion total (avg ~809 prompt / ~288 completion per call).

37. **ID guard**: 0 hits (case-id patterns live only in JSON data files; all .py files clean).

38. **KB regression**: 48/48 green (S1-S48, all dims 5).

39. **Evaluator regression**: accuracy 1.00, TP 24, TN 96, FP 0.

40. **qa_check.sh**: OK; live injections 10/10; aligner check_regress.py exit=0 (REGRESSIONS: 0; RESIDUALS: 6 known frozen residuals, not failures); disk 58 Gi free.

41. **HOVEDKONKLUSJON: CURRENT_PROOF_DOCTRINE_IS_TOO_STRICT (B).**
    21/45 oracle "errors" are C/D/E — the benchmark demands verdicts the evidence cannot carry under proof doctrine — and 33/46 benchmark labels diverge from doctrine-consistent verdicts. Rejected: A (REVIEWER_REASONING_IS_VIABLE — bounded benchmark accuracy 1/17 shows the proof-graph layer is not viable as specified), C (EVIDENCE_IS_GENUINELY_INSUFFICIENT — only 3/45 genuinely D), D (REVIEWER_REASONING_CEILING — baseline doctrine accuracy 91.7%).

42. **Sekundære medvirkende årsaker**: (a) bounded-operator gap — 17 B cases need the four-operator layer from point 14; (b) structured-proof format is over-conservative as tested — operator descriptions need worked examples; (c) validator PARTIAL-precondition narrowness converted 2 would-be-correct PARTIALs into REVIEW_REQUIRED (CAL048/CAL050).

43. **Eksplisitt IKKE videre**: do not tune the reviewer prompt against benchmark labels; do not build packet R&D, holdout-v3, blind recertification, or live dialog; never allow EXHAUSTIVE_SET_EXCLUSION without explicit markers; do not re-run the structured variant with more iterations (max-1 rule).

44. **Anbefalt neste arkitektursteg (ikke implementert)**: first split the evaluation target into a proof-doctrine score (current behavior) and a semantic-intent score (bounded-inference-permitting); then add the bounded-operator layer (TRANSITIVE_EQUIVALENCE, RULE_PLUS_CONDITION, NUMERIC_CONFLICT threshold comparison, SAME_PREDICATE_OPPOSITE_POLARITY distributional reading) in the deterministic evidence layer — not in the reviewer prompt.

## Artifact inventory

| File | Role |
|---|---|
| oracle-proof-ledger.json | 46-row audited ledger (A-F), validator-clean |
| probe-set.json | 24-case probe + 21 negative controls (schema probe-set-v1) |
| baseline-results.json | frozen v1.1 baseline copy with provenance header |
| structured-proof-results.json | 24-case structured-proof run |
| structured-proof-controls.json | 21-case C/D/E control run |
| stability-results.json | 5 claims x 3 stability runs |
| validate_proof.py / inference-operators.json / proof-validator-spec.md | deterministic validator + operator export + spec |
| run_proof_probe.py / run_stability.py | probe/stability runners (Luna, temp 0) |
| build_ledger.py / cases_data.json | ledger builder + case data (id-guard contract) |
| oracle-case-audit.md | category audit, 8-question analyses, canaries, label-issue list |
| analysis.md | headline metrics, interpretation, decision tree |
| final-report.md | this report (44 SLUTTRAPPORT points) |
