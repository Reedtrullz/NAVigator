# Final report - SEMANTIC-JUDGE-EVIDENCE-PACKET-REDESIGN

All numbers verified from files in this directory (+ ../results for B).
Label normalization applied everywhere: INSUFFICIENT_EVIDENCE ->
INSUFFICIENT, PARTIALLY_SUPPORTED -> PARTIAL.

1. **Task-lock**: TASK-LOCK.json ACTIVE during work; task_id correct; set to COMPLETED at end. No holdout-v3, no blind recert, no live-dialog, no NAV research, max A (no B), doctrine frozen.
2. **Baseline (B, frozen)**: 389 claims; auto 121 (100% SUPPORTED and CONTRADICTED precision), review 268; selective accuracy 0.8757 normalized; RR 27 (6.9%); novel-40 27/35 = 77.1% (+5 RR). Gate subset (96 claims): 90 decided, 0.8333, RR 6.
3. **Packet-error taxonomy**: 45 review errors = T1 S0-distraction 14, T2 binding failure 12, T3 retrieval ceiling 6, T4 contradiction-boundary 13 (details in packet-error-audit.md).
4. **S0 analysis**: all 14 INSUFF/PARTIAL->CONTRADICTED overreach cases cited S0 as sole contradiction evidence (conf 0.82-0.99). But S0 removal did not fix the error set (no_s0 fixed 1/45; include 0/45) and include-mode scored higher on the untouched gate subset (0.8427 vs 0.8043). S0 harms via gist-reasoning, yet full removal also removes context the reviewer uses. Mode matrix: include 0.8427, no_s0 0.8043, fallback 0.7889.
5. **Distributed evidence**: ENT-A atom 2 evidence is distributed (best single coverage 0.25). Joint-support machinery was built (greedy union >= 0.7, max 3 spans); it did not convert ENT-A (reviewer-side failure, point 6).
6. **ENT-A root cause**: packet is correct (A1 joint 0.667, A2 joint set present). Reviewer returned A1 conf 0.35 INSUFFICIENT and A2 below-threshold INSUFFICIENT. Classification: reviewer reasoning failure over distributed evidence (packet and grouping are fine; expected label SUPPORTED is correct).
7. **SUPPORTED->INSUFFICIENT root causes**: 12 binding failures (entailing span in packet, unused; flat-packet guesswork) + 5 retrieval-ceiling cases (best candidate coverage 0.33-0.57: MP-016A, MP-015A, ACT-19, D20-L5, N-S4; plus HOL005 PARTIAL variant). The redesign fixed neither class at scale (binding failures persisted; only wider top_n touched the ceiling).
8. **INSUFFICIENT->CONTRADICTED root causes**: 100% S0-gist overreach (14/14). no_s0 mode eliminated the S0 trigger; residual overreach (N-R3 CONTRADICTED) is reviewer reasoning on a neutral packet.
9. **Oracle packet design**: rule-based, per expected verdict: SUPPORTED -> top-3 non-qualifier + joint set + 1 qualifier per atom; INSUFFICIENT -> neutral non-S0 surface; CONTRADICTED/PARTIAL -> full surface incl. S0. Diagnostic only; no claim-ID mappings (spec 18/39).
10. **Oracle packet score**: 7/45 = 15.6% (SUPPORTED 0/17, INSUFFICIENT 3/9, PARTIAL 3/6, CONTRADICTED 1/13). An earlier stricter prune scored 10/45 = 22.2%. Both are far below the ~88% threshold at which §17 would blame the reviewer; here even oracle evidence does not let the frozen reviewer reach the expected verdicts.
11. **Automatic router**: pipeline per router-spec.md (atoms -> candidates(6) -> dedup -> roles -> diversity -> joint sets -> groups -> budget -> S0 policy).
12. **Per-atom grouping**: implemented; fidelity validator rejects any span outside the atom's own group (cross-group binding impossible).
13. **Role tags**: CONDITION, EXCEPTION, NEGATION, MODALITY, NUMERIC, TEMPORAL, LOCALITY, ACTOR, MAIN_RULE.
14. **Condition linking**: RULE_WITH_CONDITION via condition regex or CONDITION role.
15. **Exception linking**: RULE_WITH_EXCEPTION via exception regex or EXCEPTION role.
16. **Locality/actor linking**: tagged as LOCALITY/ACTOR roles on spans (no separate group type).
17. **Deduplication**: global canonical-text registry; duplicate spans merged, max score kept.
18. **Diversity ranking**: within-atom Jaccard >= 0.8 dropped before ranking; global budget ranks by atom-use then score.
19. **Packet-size experiment** (no_s0, gate subset): max4 0.8132, max6 0.8043, max8 0.7889. Fewer spans was mildly better; no accuracy case for larger packets.
20. **Minimum-sufficient packet analysis**: on the 45 error cases even oracle selection fails (7/45), i.e. for most of T4 the packet cannot contain doctrine-sufficient evidence for the expected verdict (implicit/absent contradiction), and for T2 the evidence was present but unused. Novel-40 oracle: 0/8.
21. **Iteration A**: implemented as specified: per-atom groups, no-S0 default, linked condition/exception, diverse ranking, deterministic aggregation.
22. **A result (gate subset, 59 live calls, 0 fidelity failures)**: subset selective accuracy 0.8043 (B 0.8333); novel-40 30/39 = 0.7692 (B 0.7714), RR 1 (B 5); decided rows correct 30 vs 27; auto FP 0/0; 2 new PARTIAL regressions in no_s0 (MP-011B, MP-024B) + N-S2 flipped SUPPORTED->INSUFFICIENT; include-mode recovered N-S2/MP-024A/MP-024B but dropped ENT-D/MP-005B to REVIEW_REQUIRED.
23. **Iteration B needed?**: No. Gate (spec 30) failed on novel-40 -> spec 43 stop rule applies.
24. **Iteration B**: not run.
25. **B result**: not applicable.
26. **Reviewer prompt diff**: exactly rules 8-11 appended (syntactic schema only); documented verbatim in packet-schema.md.
27. **Prompt/model/config freeze**: prompt_sha 7377d10307e2fb7d, model openai/gpt-5.6-luna, temp 0, max_tokens 300, packet-v2.1 - registered in every results file meta.
28. **Novel-40**: 0.7692 (30/39 decided) vs B 0.7714. Gate required > 0.771: FAILED.
29. **Novel-40 oracle score**: 0/8 on the B error subset.
30. **Gap oracle vs automatic**: ~zero router headroom on the hard cases; both ~0-7/45. The gap §24 hoped to harvest does not exist under frozen doctrine.
31. **Source entailment A-D (this stage)**: A INSUFFICIENT (fail), B INSUFFICIENT (pass), C CONTRADICTED (auto pass), D REVIEW_REQUIRED via human_review_flag (not pass; B had C/D pass). Full ENT re-run not performed (blocked by gate).
32. **ENT-A**: reviewer reasoning failure (point 6); no patch applied.
33. **ENT-B**: passes (INSUFFICIENT, correct).
34. **ENT-C**: passes (auto-path CONTRADICTED).
35. **ENT-D**: REVIEW_REQUIRED under packet-v2.1 (needs_human_review=true); mode-sensitive; prior B passed. Treat as stability risk of the schema addendum, not a doctrine change.
36. **SUPPORTED precision**: 37/37 = 1.0 (gate subset, v2).
37. **CONTRADICTED precision**: 20/21 = 0.952.
38. **INSUFFICIENT recall**: 17/20 = 0.85.
39. **Unsupported->SUPPORTED FP**: 0 (all variants).
40. **Selective accuracy**: 0.8043 v2 vs 0.8333 B (gate subset).
41. **Coverage**: 92/96 = 0.958 v2 vs 90/96 = 0.938 B.
42. **REVIEW_REQUIRED rate**: 4/96 = 4.2% v2 vs 6/96 = 6.3% B (subset); novel-40 1 vs 5.
43. **Stability**: not run - spec 35 requires a final candidate; none was accepted.
44. **Proof fidelity**: 100% - 0 fidelity failures across 295 live v2 review calls (schema followed in every call).
45. **Safety**: injection battery 10/10 live (frozen path); CAL086 stays locked under v2; 0 safety FPs anywhere.
46-49. **Numeric/temporal/modality/actor-locality**: role tags implemented; dedicated re-scores not re-run this stage (blocked by gate). No regressions observed in the sets that were run.
50. **Risk-coverage**: see risk-coverage.md - frontier is reviewer-limited; safety did not degrade.
51. **Model calls/100 claims**: ~69 (268 review calls / 389 claims), unchanged routing, no re-calls.
52. **Packet/token cost**: avg 1.24 spans, ~84 packet tokens per reviewed claim (max6) vs ~45 tokens (B error-case packets); max4 is cost-optimal.
53. **ID guard**: no claim-ID->span mappings anywhere; oracle is generic rule-based and diagnostic; packet_router.py and run_oracle.py contain no ID lookups.
54. **KB regression**: 48/48 BESTATT (score_baseline.py), KB untouched.
55. **Evaluator regression**: TP=24 TN=96 FP=0 FN=0, acc 1.00, safety_FP 0.
56. **Quote-aligner regression**: REGRESSIONS: 0 (6 known residuals, unchanged).
57. **qa_check.sh**: OK (no known error patterns).
58. **READINESS**: **NOT_READY_FOR_HYBRID_BLIND_RECERTIFICATION**.
59. **Ceilings**: per spec 17's criterion, the binding constraint is reviewer reasoning plus evidence availability (oracle 15.6-22.2% << 88%), not packet routing. Automatic router headroom over oracle is ~zero on the error set. The one clearly routing-attributable class (T1 S0) was addressed by no_s0 but yields no net gate gain.
60. **Remaining weaknesses**: (a) reviewer will not commit to SUPPORTED on distributed/paraphrased evidence even when grouped; (b) implicit-contradiction cases (T4) lack doctrine-sufficient spans - possible POTENTIAL_KB_ISSUE for CAL029/CAL030/CAL064/HOL022/MP-013B/N-O5; (c) ENT-D flips to human review under the schema addendum; (d) S0 policy is a genuine trade-off, not a free win; (e) run-to-run verdict variance at temp 0 on borderline rows (MP-015A, ENT-D).
61. **Recommended next step**: per spec 43, the owner decision is between (i) reviewer/model change (doctrine or model swap - out of scope here) or (ii) accepting a higher REVIEW rate. Recommended concrete next stage: a bounded reviewer-reasoning probe on the 17 SUPPORTED->INSUFFICIENT and 13 T4 cases using oracle packets + ablated prompts (diagnostic, not runtime), before any new iteration; do not start packet redesign v0.2.
