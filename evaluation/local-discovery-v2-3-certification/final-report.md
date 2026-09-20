# V2.3 Candidate Certification - Final Report

1. Task ID: NAV-EXPLORE-LOCAL-DISCOVERY-V2_3-CANDIDATE-CERTIFICATION
2. Candidate SHA: b4567824f054af811f4c944daa8455d3a4b29e11b7916ebb9561d98061fe1af2
3. Candidate files matching: 19/19
4. Candidate modified during certification? No; byte-verified before and after.
5. Protocol SHA: fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca
6. Protocol changed? No.
7. Provider config integrity: provider-config-v2-3.json SHA 51ee5b28f62fea423e0f83bfb28eaa3ebe652ea91aefad7ed2ddbbbe2a714586, unchanged and matching the frozen manifest.
8. Historical write incident occurred? Yes. HISTORICAL_WRITE_INCIDENT = TRUE, permanently registered (not hidden behind historical_files_modified = 0).
9. Historical file currently restored? Yes; historical providers.py restored.
10. Restoration SHA verification: restored providers.py SHA 54b38921b02736763d3baef25e7bb860f1bf1b9f8d3b0fb3ac58b0808083806a equals the V2.1 implementation-snapshot manifest entry (see candidate-integrity.json); V2.1 snapshot verified 7/7 files.
11. Residual historical differences: none; restored byte-identical.
12. V2.3 lineage isolated from historical mutation? Yes. SiteDirectProviderV23 and max_urls=16 are confined to candidate runtime (cli_v23.py); zero V23 references in historical providers.py.
13. Integrity adjudication: RESTORED_WITHOUT_CANDIDATE_CONTAMINATION.
14. Original benchmark attempts: 117 (frozen historical artifact, not re-executed).
15. Original benchmark success: 108.
16. Original benchmark failures: 9, exactly the Raelingen queries Q-raelingen-1..9; original gate FAIL_108_OF_117 preserved.
17. Availability contract frozen? Yes; source-availability-adjudication-contract.md frozen before probes.
18. Raelingen cases adjudicated: all 9 as RUNTIME_FAILURE_OR_UNRESOLVED.
19. External-source-unavailable N: 0.
20. Runtime-internal failure N: 9 (historical benchmark adjudication; 0 in certification re-runs).
21. Unresolved N: 0.
22. Available-source denominator: 117.
23. Success on available sources: 108/117.
24. Critical false-no-route: 9 at benchmark level; 0 at route level (live/replay).
25. Unsupported FULLY_VERIFIED: 0.
26. Fail-closed behavior: yes; NO_RESULTS status, no fabricated results.
27. Evaluation harness incident occurred? Yes. EVALUATION_HARNESS_INCIDENT = TRUE, permanently registered (initial 0/22 replay was harness-only).
28. Harness root cause: runner routing bug in the temporary certification harness; not a candidate defect.
29. Candidate contaminated by harness issue? No; clean re-run 22/22 and candidate SHA unchanged.
30. Clean replay: 22/22 route matches.
31. V1 tests: 49 passed.
32. V2 tests: 27 passed.
33. V2.1 tests: 19 passed.
34. V2.2 tests: 20 passed.
35. V2.3 tests: 15 passed.
36. Total tests: 130/130, no fixes applied during certification.
37. Live burned N: 13 attempted.
38. Live complete: 12.
39. Live source-unavailable: 1 incomplete (Raelingen), adjudicated as runtime defect, not external unavailability.
40. Live internal failures: 0.
41. Provenance completeness: 100% for authorizing assertions (12/12 COMPLETE runs); the incomplete Raelingen run honestly reports DISCOVERY_INCOMPLETE / ROUTE_UNVERIFIED.
42. External search calls: 0.
43. External credential required? No; presence-only checks, no credential values read.
44. Security: PASS (security-report.md; no secret values read or persisted).
45. Fresh municipalities used: 0.
46. Original deviations preserved in record? Yes; deviations_preserved in candidate-certification.json includes FAIL_108_OF_117, HISTORICAL_WRITE_INCIDENT, and EVALUATION_HARNESS_INCIDENT.
47. Certification gates passed (11): candidate integrity 19/19, historical restoration, protocol unchanged, provider config unchanged, tests 130/130, replay 22/22, live attempts 13/13, unsupported-FV 0, provenance 100% (authorizing assertions), external search 0, fresh municipalities 0.
48. Certification gates failed (3): complete-or-adjudicated 13/13, runtime-internal-failures 0, critical-false-no-route 0.
49. Candidate certification artifact: candidate-certification.json.
50. STATUS: V2_3_CERTIFICATION_FAIL_RUNTIME_CHANGE_REQUIRED.
51. Is fresh holdout now justified? No. The candidate has a known runtime implementation defect and must not enter fresh evaluation.
52. Remaining limitations: (a) runtime/discovery_v2/roots.py builds the platform root on bedinnsats.no while its docstring, frozen provider-config-v2-3.json, and the gold corpus specify bedreinnsats.no; (b) provenance for the non-authoritative bedinnsats host is unknown - it resolves NXDOMAIN today but historical attempt logs recorded OK, so external DNS drift is possible and was out of scope for probing; (c) this certification is burned-data-only evidence.
53. Recommended next bounded stage: a V2.4 lineage task (separate task, new candidate) that repairs the roots.py platform host pattern to bedreinnsats.no, freezes a new candidate, and re-runs the frozen benchmark before any fresh evaluation is considered.

STOPP. No fresh eval, no runtime patch, no Protocol V1 change, no historical rewrite.
