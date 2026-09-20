# Final Report - NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1

1. Task ID: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1
2. Starting Wave-1 SUT SHA: runtime/sut/phase2/pipeline.py 2c9eba079b57877f109ea94370f28d2ae7f7238020c20592f1eafad662206056 (Wave-1 frozen candidate; full 24-component pin e19dd2d6d5329ef3fe85e1719fdc879717563a2e18dc561812b5e6d2a7035f27)
3. Starting Wave-1 manifest SHA-256: e19dd2d6d5329ef3fe85e1719fdc879717563a2e18dc561812b5e6d2a7035f27
4. Post-Wave-1 analysis SHA: evaluation/full-sut-post-wave1-residual-failure-analysis-v1/final-report.md 1484f9f15bc35ae60368e083dfd668f48d086960252eab972b1ac3c0cde9e820 (hashes.txt pin e8d4167c0fa08a820090be3ccedf28c477a62a4eb17ac30dfb60f30556e28738)
5. Gate 0: PASS (gate0-report.json: 14/14 import smoke, baseline 170 tests passed, control-character scan clean over 31 files, environment pinned Python 3.14.6 / pytest 9.0.3)
6. RC-08 proven root cause: retrieval scored all 61 KB docs regardless of track; docs carried hardcoded "general" domain; pipeline overwrote domain post-hoc; planner INFO blocks were unfiltered; index had no domains metadata. Proven in rc08-root-cause.md mechanisms A/C/D/F/G. Post-candidate-1 replay added a second proven RC-08-scope defect: per-track evidence_id renumbering collided across tracks on multi-track queries (21 fail-closed executions; rc08-candidate2-repair.md).
7. RC-08 source changes: data/knowledge-index-v1.json (domains arrays, one-shot rc08-add-doc-domains.py; b83a0808... -> c8de229b...), runtime/sut/phase2/knowledge.py (domain-scoped candidate filtering, per-record domains, domain-scoped gap reserve), runtime/sut/phase2/pipeline.py (no domain overwrite; s4 global evidence_id/record_id renumbering across tracks preserving K-R/K-D prefixes - candidate-2 fix), runtime/sut/phase3/planner.py (INFO blocks scoped by track-domain intersection)
8. RC-08 tests: runtime/sut/phase2/test_knowledge_scoping.py 13/13 + runtime/sut/phase2/test_pipeline_ids.py 1/1 (two-track uniqueness), both PASS
9. Retrieval track-scope invariant: every record retrieved for a track intersects that track's domain; record/evidence ids globally unique per answer; verified by test_knowledge_scoping.py and test_pipeline_ids.py
10. Replay contamination diagnostics: cross-track INFO leakage removed; diagnostics count same-track multiple "Nasjonal informasjon" blocks (103 cases) explicitly as NOT contamination (RC-08 scope was cross-domain only); 625 info blocks total; renderer dedup (RC-06) remains deferred
11. RC-07 proven root cause: POINT_IN_TIME snapshots out-scored CURRENT docs for generic queries (R1 empty routes); route targets extracted from any quoted/bold fragment incl. numeric facts (R2 junk routes); track binding mismatched secondary-track retrieval (R3). Proven in rc07-root-cause.md with route-selection-dataflow-before.md probe evidence
12. RC-07 source changes: runtime/sut/phase2/knowledge.py (CURRENT-first slot ordering), runtime/sut/phase2/routes.py (reject digit-bearing route-target candidates = no numeric/temporal facts as service names), runtime/sut/phase3/planner.py (consistent track-domain binding)
13. RC-07 tests: test_route_targets.py 10/10 + test_planner_scoping.py 2/2, PASS
14. Route-target structured invariant: emitted route labels are service concepts with resolved provenance; structured routes carry route_evidence with provenance_ids (RC-10 helpers); no-route fail-closed behavior unchanged
15. Empty route count: 100/120 cases with empty routes (raw count; composition note under item 17). Wave-1 raw comparison: 97 empty, but Wave-1's 23 non-empty contained 8 junk-only and 12 fragment-content routes (~3 genuinely valid); Wave-2's 20 non-empty are provenance-backed with 0 junk and 2 fragment-like labels - effective valid route coverage improved substantially while junk emission is suppressed
16. Junk route count: 0 (Wave-1: 8 junk-only cases; suppression working; raw empty count is the honest trade-off of suppression)
17. Fragment-like route count: 2 (ROUT-072 "Hensikt" among 3 labels, ROUT-083 "URL"; lexical-ceiling residual documented in remaining-findings.json; not hidden, not gated as failure)
18. RC-10 proven root cause: frozen output had flat evidence pool with no per-route/per-claim ownership links; 23/38 zero-evidence cases had provenance URLs never attached; 15/38 had no provenance entries (retrieval-contamination downstream); safety_priority never mirrored into evidence. Proven in rc10-evidence-dataflow.md
19. RC-10 source changes: runtime/sut/phase2/pipeline.py (shared _route_evidence/_claim_evidence helpers, additive evidence.route_evidence/claim_evidence maps - schema-safe, routes stay labels-only per frozen scorer contract), runtime/sut/phase3/finalize.py (attachment at finalize)
20. RC-10 tests: test_evidence_attachment.py 11/11 PASS
21. Route provenance result: 20/20 route-bearing cases have provenance for every route label; 0 structured routes without provenance; 0 cases with routes but no provenance (mechanism gate PASS)
22. Claim provenance result: 673/673 claim_evidence claims carry provenance (100%)
23. RC-11 proven root cause: internal fine 12-class triage existed but both emission points collapsed it via "if priority not in OUTPUT_VALUES: priority = ACUTE_RISK_NOW", discarding exact categories (19/20 Wave-1 safety criteria failed exact-category string; over-triage dominant, no under-triage). Proven in rc11-safety-vocabulary-root-cause.md
24. RC-11 source changes: runtime/sut/phase2/pipeline.py + runtime/sut/phase3/finalize.py emission points now emit the fine 12-class at top level; nested safety.priority keeps collapsed 3-level frozen-scorer value; evidence.safety_priority mirrors fine class; safety.py untouched
25. RC-11 tests: test_safety_output.py 9/9 + test_safety_granularity.py 9/9 (pinned expectation updated) PASS
26. Acute safety invariant: EMERGENCY_TRIGGER_LOGIC_CHANGED=false; safety.py unchanged; acute triggers incl. negated acute phrasing fail closed to ACUTE_RISK_NOW as before; no under-triage introduced (suite + canaries)
27. Safety category distribution (official replay, top level): NON_ACUTE_ROUTINE 101, ACUTE_RISK_NOW 4, ACUTE_SOMATIC_MEDICAL 4, ABUSE_DISCLOSURE_REPORTING 3, and one each of ACUTE_RISK_HIGH_THIRD_PARTY, SAFETY_CONCERN_NO_ACUTE_VIOLENCE, URGENT_PSYCHOSIS_SUSPECT, SAFETY_CONCERN_REPORTING, ACUTE_RISK_HIGH, ACUTE_RISK_UNSURE_TRIAGE, URGENT_CARE_CAPACITY, SYSTEM_SAFETY_PRECEDENCE - fine 12-class now observable end-to-end
28. Full test-suite result: 216/216 passed, 0 failed/errors (python3 -m pytest runtime/sut/ -q; 170 pre-Wave-2 + 46 new/updated)
29. Phase 1 regression: test_input_normalization.py 17/17, test_schemas.py 13/13, test_context.py 11/11 PASS (RC-01/02/03 behavior intact)
30. Phase 2 regression: aggregate 9, decompose 15, discovery_adapter 7, knowledge 10, knowledge_scoping 13, pipeline 10, pipeline_ids 1, route_targets 10, routes 8, safety 26 - all PASS
31. Phase 3 regression: test_phase3.py 22/22, test_planner_scoping.py 2/2 PASS
32. Wave-1 regression tests: all Wave-1 test files retained and passing inside the 216-test suite; national-route tests 10/10, safety granularity pinned expectation updated only for the authorized RC-11 fine-class emission
33. Evaluator imports into product: 0 runtime hits (test_separation.py enforces the invariant; grep over runtime/sut shows only test files)
34. Candidate source SHA: runtime/sut/phase2/pipeline.py 73cd0350625a0424d3e20723d915270b0b72f8cacd8e655303ebce598e027429 (candidate-2); full 24-component SHA list in hashes.txt
35. Candidate manifest SHA: repaired-sut-manifest.json 8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e (candidate_version v2, frozen_candidate_attempts 2 of max 2)
36. Candidate attempts: 2 of 2 (v1: four RCs in one pass, replay 99/120 with 21 fail-closed from cross-track evidence_id collision - superseded; v2: bounded id-renumbering fix + regression test, official replay 120/120 - final allowed attempt)
37. 120-case structural replay: YES, official run runs/structural-120-replay-v2/ (gold-blind)
38. Replay success count: 120/120 SUCCESS
39. Crashes: 0
40. Schema validity: 120/120 outputs valid per frozen sut-output.schema.json
41. Input failures: 0 input hard failures; 104 recoverable local-discovery RECOVERABLE states (fail-closed as designed, matching Wave-1 semantics)
42. Cross-track contamination diagnostics: 0 cross-track INFO leakage mechanism remaining (domain-scoped planner INFO + globally unique evidence ids); multi-block same-track national info counted separately as presentation noise (RC-06 deferred, not contamination)
43. Structured routes: 24 route entries across 20 route-bearing cases, 14 distinct labels
44. Unprovenanced routes: 0
45. no_route consistency: 0 mismatches between no_route_asserted and empty/non-empty routes (100 empty/true, 20 non-empty/false)
46. Determinism: PASS - independent full rerun into runs/determinism-check-v2/; 120/120 prediction files byte-identical by SHA-256
47. Historical predictions mutated: NO
48. Measurement V3 run: NO
49. Gold used by product: NO
50. RC-09 implemented: NO (deferred, re-derive after Wave-2 re-measurement)
51. RC-12 implemented: NO (deferred per analysis)
52. Broad RC-04 implemented: NO
53. Broad RC-06 implemented: NO (renderer dedup deferred; only upstream scoping changed)
54. Overfit findings: none; no case IDs or corpus strings in runtime (id-guard grep clean); RC-07/RC-08/RC-10/RC-11 fixes are generic mechanisms (domain scoping, identity uniqueness, CURRENT-first ordering, fragment rejection, attachment plumbing, vocabulary emission) driven by frozen decompose vocabulary and schema contracts, not by individual expected verdicts
55. Remaining known issues: ROUT-072/ROUT-083 fragment-like route labels (lexical extraction ceiling); SAF-008 collapsed-urgency level unchanged by design (RC-11 changed emission, not triage logic); same-track multiple INFO blocks (RC-06 deferred); ROUT-042 forbidden residual LABEL_SENSITIVITY_KNOWN excluded from sizing; 18 UNRESOLVED measurement-lane rows are state semantics, not product mechanism; grounded route-target extraction remains lexical; discovery/local route path unchanged. Per-criterion improvement expectations in remaining-findings.json are EXPECTATIONS, not measurements
56. STATUS: FULL_SUT_REPAIR_WAVE_2_READY_FOR_REMEASUREMENT
57. Recommended next bounded task: owner-authorized NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2 against the frozen candidate (manifest 8369e21309d7b53413bb6ab93ba7e0983769e707ca7680803237edc1a39ee22e); no further runtime changes in this task (candidate-2 was the final allowed attempt)
