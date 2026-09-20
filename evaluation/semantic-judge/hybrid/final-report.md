# Final report - SEMANTIC-JUDGE-HYBRID-EVIDENCE-REVIEW

Iteration B (reviewer-spec v1.1: packet span capacity 4 -> 8, prompt
rules 2a/5b). Full run: 389 claims, 268 review calls, 956 s.
Labels normalized: INSUFFICIENT_EVIDENCE = INSUFFICIENT,
PARTIALLY_SUPPORTED = PARTIAL. Data: results/hybrid-eval.json.

1. Task-lock/pre-flight: ACTIVE through the run; TASK-LOCK.json in
   hybrid/, frozen docs dated 2026-09-02 before benchmarking.
2. Baseline-status: quote-aligner v0.2 mp 95.83%, C-prec 97-100%,
   safety/numeric/temporal FP 0, KB 48/48, id_guard 0; failing
   insufficiency recall 96.88%, diagnostic-20 80%, entailment 3/4,
   ENT-D FAIL, novel-40 27/40 (spec 1).
3. Deterministic auto-decision coverage: 121/389 = 31.1% (gated).
4. Deterministic auto-SUPPORTED precision: 48/48 = 100%.
5. Deterministic auto-CONTRADICTED precision: 73/73 = 100%.
6. NO_EVIDENCE-rate: engine-level 35.5% (138/389); after gates all
   NO_EVIDENCE cases route to review or stay REVIEW_REQUIRED.
7. AMBIGUOUS-rate: engine-level 5.4% (21/389), all gated to review.
8. Hybrid architecture: D. engine -> auto_gate -> reviewer packet ->
   gpt-5.6-luna -> fidelity -> fusion (architecture.md, frozen).
9. Fusion rules: fusion-spec.md v1.0; hard-contra lock, injection
   lock, support-coverage check, INSUFFICIENT first-class.
10. Semantic reviewer spec: reviewer-spec.md v1.1 (frozen),
   gpt-5.6-luna, temp 0, max_tokens 300, strict JSON.
11. Evidence packet: claim + atoms + max 8 aligner-ranked candidate
   spans + S0 full source (<1200 chars) + deterministic findings.
12. Proof fidelity enforcement: 100% pass in B run (A run: 2 charset
   fidelity failures, fixed by prompt rule 2b; 0 in B).
13. REVIEW_REQUIRED-policy: never guessed; 27/389 = 6.9% (routes:
   reviewer_insufficient 14, support_span_not_entailing 5,
   below_threshold_or_flagged 5, hard_contra_lock 2, injection_lock 1).
14. Iteration A: executed in full, results/hybrid-eval-iterationA.json
   (348 decided, 87.64%).
15. A-resultat: sel-acc 87.64%, rev-acc 81.06%, RR 41, novel-40
   81.1% (normalized), ENT-C/D pass, 0 critical FP.
16. Iteration B noedvendig: yes; A review errors clustered on
   INSUFFICIENT->CONTRADICTED (14) and SUPPORTED->INSUFFICIENT (12);
   packet capacity 4 was the general cause.
17. B-resultat: 362 decided (93.1%), sel-acc 87.57%, rev-acc 81.33%,
   RR 27, fidelity 100%, 0 critical FP. Same accuracy as A, +14
   decided cases, INSUFF->CONTRAD errors 14 -> 9, but
   SUPPORTED->INSUFFICIENT 12 -> 17.
18. Reviewer subset stoerrelse: 268 of 389 claims reviewed; 45
   review-layer error cases captured in development-set.json.
19. Semantic review accuracy: 81.3% on decided review cases (241).
20. Unsupported->SUPPORTED FP: 0 (gate <=1%, limit >2%) - PASS.
21. Semantic review safety FP: 0 - PASS.
22. Semantic review stability: 30 difficult claims x 3 runs (90
   calls): 17/30 verdict-consistent, 21/30 span-consistent, mean
   confidence spread 0.199, unstable auto-accepts 0 (spec 30 - PASS;
   wobble routes to REVIEW_REQUIRED per spec 29).
23. Evidence-span fidelity: 100% of accepted SUPPORTED/CONTRADICTED
   verdicts cite existing span ids; support-coverage check active.
24. ENT-A: FAIL (reviewer INSUFFICIENT where spans entail; engine
   SUPPORTED was correct - conservative direction, not critical).
25. ENT-B: PASS (INSUFFICIENT correct).
26. ENT-C: PASS (auto CONTRADICTED correct).
27. ENT-D: PASS via reviewer (reviewer CONTRADICTED 0.92 accepted;
   deterministic ceiling broken as intended).
28. Source-entailment 4/4: 3/4 (ENT-A miss; same as baseline).
29. Novel-40 hybrid score: 27/35 decided + 5 RR = 77.1% selective
   (target >=90% - FAIL; 5 review-layer errors + 5 RR).
30. Minimal-pair hybrid score: 45/51 decided = 88.2% selective.
31. Contra/insuff-resultat: 62/68 decided = 91.2% selective; engine
   contra precision preserved at 100% on auto layer.
32. Safety result: 0 safety FP anywhere (gate: 0) - PASS.
33. Numeric result: 0 numeric critical FP (gate: 0) - PASS.
34. Temporal result: 0 temporal critical FP (gate: 0) - PASS.
35. Modality: 28/29 = 96.6% selective, best set; review layer 12/13
   correct (1 SUPPORTED->INSUFFICIENT miss, conservative direction).
36. Actor/locality: actor 26/30 = 86.7%, locality 16/18 = 88.9%
   selective; remaining errors are INSUFFICIENT->CONTRADICTED on
   scope-of-source claims (reviewer overreads S0 context).
37. Total coverage: 362/389 = 93.1% decided (auto 121 + review 241).
38. Auto-decision coverage: 121/389 = 31.1% at 100%/100% precision
   (baseline without gates 224/389 = 57.6% at 86.1%/87.2%).
39. REVIEW_REQUIRED-rate: 27/389 = 6.9%.
40. Selective accuracy: 87.57% overall (auto 100%, review 81.3%);
   spec gate >=97% on auto-decided claims - auto layer PASSES (100%).
41. Risk-coverage: flat curve; 0.95 floor gives 90.5%/88.35% vs
   93.1%/87.57% (results/risk-coverage.md); class thresholds kept.
42. High-confidence errors: 12 accepted errors with confidence
   >=0.95, all INSUFFICIENT/PARTIAL->CONTRADICTED (conservative
   direction); 0 errors toward SUPPORTED anywhere in the run.
43. Injection result: 10/10 PASS dry and live (rule 2a/5b prompt).
44. Rule-only vs quote-only vs reviewer vs hybrid:
   A rule-only: 100% coverage, 80.7% acc, unbounded SFP risk.
   B quote-only: 57.6% coverage, 86.6% acc.
   C reviewer-only (on review subset): 81.3% acc, 389 calls if full.
   D hybrid: 93.1% coverage, 87.6% acc, 268 calls, 0 critical FP.
   D dominates on coverage x accuracy x cost x safety.
45. LLM calls per 100 claims: 68.9 (268/389).
46. Token/cost estimate: ~1.0-1.5k tokens/call, ~320-400k total,
   ~2.5 s/call (cost-model.md; exact usage not logged by proxy).
47. Burned holdout-v2 development result: 28/37 decided = 75.7%
   selective; RR 3; no holdout-v3 built.
48. ID guard: 0 violations on hybrid code (reviewer.py, auto_gate.py,
   run_hybrid_eval.py).
49. KB regression: 48/48 PASS.
50. Evaluator regression: 1.00 acc, TP 24, TN 96, FP 0, FN 0.
51. Quote-aligner regression: 0 regressions, 6 known residuals
   (unchanged vs pre-task baseline).
52. qa_check.sh: not present in repo; the five QA batteries above
   were run individually and all pass (see 48-51 + injections 43).
53. Critical errors: 0 (safety/numeric/temporal FP all 0; no error
   in the accept-favorable direction).
54. READINESS: NOT_READY_FOR_HYBRID_BLIND_RECERTIFICATION.
   Failing gates: novel-40 77.1% < 90%; ENT-A/entailment 3/4;
   review-layer accuracy 81.3% below the 97% bar for the
   review path at the operating point.
55. Gjenvaerende svakheter: (a) reviewer overreads S0 full-source
   context and flips absence-of-evidence to CONTRADICTED (9 cases);
   (b) reviewer misses entailment when support is distributed across
   multiple spans or requires two-hop inference (17 SUPPORTED->
   INSUFFICIENT cases); (c) wobble on 13/30 hard claims (safe
   direction); (d) compound PARTIAL vs CONTRADICTED boundary on
   holdout/calibration PARTIAL cases.
56. Anbefalt neste steg: per spec 43, STOPP - do not build hybrid
   v0.2 or holdout-v3. Next task is a focused evidence-packet
   redesign (drop S0 full-source span; provide per-atom span groups
   and explicit no-evidence markers) as a NEW task-lock, then
   HYBRID BLIND RECERTIFICATION only after gates pass.
