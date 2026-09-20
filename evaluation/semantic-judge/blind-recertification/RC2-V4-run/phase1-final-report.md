# RC2-V4 Phase 1 SLUTTRAPPORT

1. Task lock: TASK-LOCK.json ACTIVE, phase PREDICTION_BEFORE_KEY,
   answer_key_access=false, scoring_allowed=false
2. Fresh session/firewall: fresh keyless session (new thread, no
   blind-key history); 0 subagents; firewall respected end to end
3. RC2 manifest SHA-256:
   1215f0d2978d80cf383f921155933f19f85f259279d04136ad00fd9f81d559cc
4. RC2 components expected/matched before: 10/10 (hashes.txt verified)
5. Blind V4 blind-cases SHA-256:
   ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d
6. Answer-key.sealed SHA-256:
   65f72b170cb200b804cf817c32aaf42e9166a20ed002777a5d9f5e71b99fd80d
7. Construction-audit.sealed SHA-256:
   5be70e666493d3a6e000b89418a8064099f03ee797ece3365840acb7a7646ff3
8. Firewall manifest status: PASS on all explicit checks (public V4
   manifest field reads SEALED_AND_FIREWALLED; no READY-suffixed value
   exists in any public manifest)
9. CORE expected: 160
10. CORE outcomes: 160
11. Missing: 0
12. Extra: 0
13. Duplicates: 0
14. Runtime successes: 160
15. Runtime failures: 0
16. Deterministic-only: 33
17. Reviewer-used: 127
18. Model calls: 127
19. Retries: 0
20. Runtime/tokens: wall time 10m59s (12:06:58-12:17:57 +0200);
    token usage not instrumented by the frozen pipeline (no runtime
    modification was permitted to add metering)
21. Product prediction distribution: AUTO_SUPPORTED 17,
    REVIEW_REQUIRED 143
22. Semantic prediction distribution: SUPPORTED 33, CONTRADICTED 24,
    REVIEW_REQUIRED 103
23. Proof prediction distribution: SUPPORTED 17,
    INSUFFICIENT_EVIDENCE 143
24. Auto count: 17
25. Review/abstain count: 143 review (RC2-FUSION-V1 produces no
    separate abstain bucket)
26. Internal proof-valid count: 17 (proof_valid=true, route=auto)
27. Atom outputs retained: YES - engine atom_results on all 160 rows
    (202 atoms), gate reasons, reviewer outputs (127), fusion routes;
    RC2 runtime produces no separate atom-prediction field beyond
    atom_results, retained as-is per spec 15
28. Reserve executed: 0 (blind-cases.json contains no reserve IDs)
29. Prediction file: RC2-V4-predictions.json (read-only)
30. Prediction SHA-256:
    49ab4e0d890cd3e9c15b44646c0235db3413647b971ba5b736888e651aa861a2
31. Raw SHA-256: same as prediction SHA (raw intermediates embedded in
    the prediction artifact; no separate raw file)
32. Prediction hash stable: TRUE (rehash identical post-QA)
33. RC2 hashes after: ALL MATCH (10/10)
34. V4 hashes after: unchanged (blind-cases, answer-key.sealed,
    construction-audit.sealed, blind-manifest, RC2 manifest +
    hashes.txt); 19/19 pre-run snapshot files byte-identical
35. Answer key accessed: NO
36. Construction audit accessed: NO (hash-only touch)
37. Blind key available: NO
38. Scoring performed: NO
39. Tuning performed: NO
40. Runtime modified: NO
41. QA: RC2 integrity before/after, V4 integrity before/after,
    firewall allowlist check, prediction schema/field completeness,
    160-ID check with order preservation, reserve exclusion,
    prediction SHA + stability, snapshot recheck; no QA command read
    labels; KB/evaluator regressions not rerun here (gate evidence is
    in the RC2 manifest development_gate_summary; blind-independent)
42. PHASE1 STATUS: PREDICTIONS_FROZEN_BEFORE_KEY
43. Next action: Phase 2 in a separate continuation receives
    BLIND_RC2_V4_KEY; this thread does not request or hold the key.
