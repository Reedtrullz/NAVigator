# Final Report - NAV-EXPLORE-RC2-BLIND-V4-FIREWALL-RESEAL

1. Task lock: ACTIVE (`TASK-LOCK.json`); RC2/RC1 execution and all tuning forbidden
2. V3 hashes unchanged: `blind-cases.json` byte-identical (SHA-256
   `ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d`)
3. V3 RC2 exposure: RC2 never executed on the V3 blind set
4. V3 eligibility status: `SEALED_BUT_NOT_CERTIFICATION_ELIGIBLE`
   (see `../V3-certification-eligibility-audit.md`)
5. V3 leakage issue: 16 per-case label-bearing plaintext files existed
6. V3 atom-key issue: atom rows existed for only 10 adjudicated CORE cases
7. V4 case reuse count: 282/282 (160 CORE + 122 reserve), zero changes
8. Cases replaced: 0
9. V4 CORE N: 160
10. V4 reserve N: 122
11. Compound CORE count: 62
12. Compound cases with complete atoms: 62/62
13. Total atom count: 141
14. Atom pass1/pass2 agreement: semantic 120/125 = 0.96; proof_safe 117/125 = 0.936
15. Atom adjudications: 10 adjudicated + 9 adjudicated_structural (19 total)
16. Unresolved atom disputes: 0
17. Top-level/atom consistency: deterministic aggregation; 1 inconsistency of 160
    (0.625% < 5% STOP gate: PASS)
18. Top-level labels changed: 1 relabel (identity and details sealed in
    `construction-audit.sealed`)
19. Criticality completeness: 160/160 (40 critical / 120 standard)
20. Subgroup metadata completeness: 160/160, all 11 flags present
21. Label-bearing files found before cleanup: 24 flagged; 16 true per-case
22. Construction evidence encrypted: yes (`answer-key.sealed` +
    `construction-audit.sealed`)
23. Plaintext label-bearing files remaining: 0
24. Full-project leak scan: 0 true leaks; 8 incidental allowlisted files documented
    in `label-leakage-inventory.json`
25. Phase-1 allowlist: `blind-cases.json`, `blind-cases.schema.json`,
    `blind-manifest.json`, `phase1-firewall-manifest.json`, plus the frozen RC2
    runtime covered by `hashes.txt`
26. Phase-1 forbidden/sealed paths: `answer-key.sealed`,
    `construction-audit.sealed`, `construction-v4/`, `RC2-V3-set/construction/`,
    `RC2-V3-set/pilot/`
27. V3 key retired: yes (fingerprint checked; key material not stored)
28. New V4 key generated: yes, memory-only
29. V3 key reused: NO
30. AES-256-GCM: yes, both envelopes
31. AAD convention: answer key = UTF-8 blind-cases SHA-256 hex (envelope AAD field
    urlsafe-b64 of the hex-string bytes); construction audit = ASCII
    `construction-audit:v1`, fresh nonce, separate envelope (envelope AAD field
    urlsafe-b64 of that ASCII string); fresh in-memory decrypt re-verified
    2026-09-04 for both envelopes
32. Blind-cases SHA: `ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d`
33. Answer-key SHA: `65f72b170cb200b804cf817c32aaf42e9166a20ed002777a5d9f5e71b99fd80d`
34. Construction-audit SHA: `5be70e666493d3a6e000b89418a8064099f03ee797ece3365840acb7a7646ff3`
35. Encryption roundtrip: verified OK for both envelopes before plaintext deletion
36. Key persisted: NO (memory-only; not in repo, disk, or Obsidian)
37. RC2 hash before: ALL OK (10/10 entries)
38. RC2 hash after: ALL OK (10/10 entries), post-seal re-verified 2026-09-04
39. RC2 unchanged: yes (frozen; no tuning, no component edits)
40. RC2 executed: NO
41. Thresholds unchanged: yes (see `certification-metrics.md`)
42. Compound metric now scoreable: yes (62/62 complete atoms)
43. Critical metric now scoreable: yes (160/160 criticality)
44. All subgroup metrics scoreable: yes (11/11 flags complete)
45. QA regression result: live gate PASS; 7/7 regressions PASS
46. STATUS: `SEALED_AND_FIREWALLED_READY`
47. Exact blockers: none
48. Recommended next step: the owner starts Phase 1 (RC2 prediction run) in a
    fresh key-free session against the allowlisted files, then unseals and scores
    with the unchanged thresholds. RC2 must not be executed outside Phase 1.
48. Recommended next step: the owner starts Phase 1 (RC2 prediction run) in a
    fresh key-free session against the allowlisted files, then unseals and scores
    with the unchanged thresholds. RC2 must not be executed outside Phase 1.

## Post-seal corrections (documentation only, 2026-09-04)

After the seal, documentation defects were corrected: the AAD envelope-field
description (stored field is urlsafe-b64 of the hex-string bytes, not of the raw
digest), the subgroup mapping note, and added in-memory decrypt-verification
records. The sealed artifacts (answer-key.sealed, construction-audit.sealed,
blind-cases.json) are byte-identical before and after these edits (SHAs
re-verified); spec 35 immutability applies to set content and is intact.
