# Final Report - NAV-EXPLORE-RC3-GENERALIZATION-HOLDOUT-CONSTRUCTION

1. Task ID: NAV-EXPLORE-RC3-GENERALIZATION-HOLDOUT-CONSTRUCTION
2. RC2/RC3 history integrity: RC2 official-score.json sha256
   e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2
   re-verified intact; RC2 release candidate, V4 artifacts, RC3
   architecture-repair artifacts and burned-V4 shadow results untouched.
3. V4 burned status: BURNED_BLIND_DEVELOPMENT_ONLY; used only as
   provenance for metric definitions; never a tuning target.
4. 0-invalid-vs-47%-auto root cause: different metric layers - the old
   invalid-proof counter measured structural validator failure only,
   auto precision measured proof-safe correctness of the conclusion.
   Recomputed separated metrics: M1 0, M2 0, M3 37, M4 18, M5 18.
5. Structural proof validity: proof object exists, registered
   proof_type, literal source span (or registered comparator rule).
6. Groundedness: every span/premise byte-exact within the authorized
   evidence packet; no out-of-packet ids or untraceable premises.
7. Semantic proof soundness: the conclusion follows from the evidence
   under the evaluation contract at atom granularity, independent of
   M1/M2.
8. Proof-safe auto correctness: case-level; an auto is unsound when the
   sealed proof-safe target does not allow exactly that polarity.
9. Metric instrumentation changed: yes - METRIC_CONTRACT_REPAIR_ONLY
   (proof-soundness-contract-v2, evaluation terminology only).
10. Runtime changed: NO. Snapshot hash-verified after all work.
11. Burned V4 reconciled structural-invalid count: 0.
12. Burned V4 ungrounded count: 0.
13. Burned V4 semantic-unsound count: 37 (atom granularity).
14. Burned V4 proof-safe-unsound-auto count: 18.
15. Snapshot name: NAV-EXPLORE-RC3-GEN-SNAPSHOT-A
    (FROZEN_FOR_GENERALIZATION_HOLDOUT_ONLY).
16. Snapshot manifest sha256:
    34a9d20d778968d21929f26760980a48563df5859b34b8697dbe520c7cae8a00.
17. Snapshot component hashes: runtime-snapshot/hashes.txt (14
    components, all verified OK post-work).
18. Snapshot frozen before authoring: yes (manifest frozen_at
    2026-09-04T18:21:49+02:00, before case_list authoring runs).
19. Candidates generated: 231.
20. Eligible pool: 231 (0 invalid, 0 novelty rejects).
21. CORE: 159.
22. Reserve: 72 (validated, not sealed, not part of the holdout).
23. Track A (representative): 75.
24. Track B (reasoning stress): 84.
25. Semantic distribution: S 40 / C 39 / P 40 / I 40.
26. Product distribution: AUTO_SUP 40 / AUTO_CON 39 / REVIEW 40 /
    ABSTAIN 40.
27. Genuine insufficiency: 40.
28. REVIEW_REQUIRED (genuine): 40.
29. ABSTAIN_INSUFFICIENT (genuine): 40.
30. Compound: 52.
31. Total expected atoms: 119 (all with full canonical keys).
32. Negation/deontic/modality: 47.
33. Condition/exception: 34.
34. Multi-span: 54.
35. Numeric: 79.
36. Temporal: 50.
37. Actor: 48.
38. Scope/locality: 28.
39. Critical: 25.
40. Semantic agreement: 91.82% (gate >=90% PASS).
41. Proof-safe agreement: 91.19% (gate >=90% PASS).
42. Product agreement: 90.57% (gate >=90% PASS).
43. Atom-count agreement: 100% (gate >=90% PASS).
44. Atom semantic agreement: 88.5% case-level / 95.8% atom-level
    (pre-adjudication); 4-5 disputed compounds adjudicated.
45. Adjudication rate: 11.95% (cap 35%) - 19/159.
46. Unresolved disputes: 0.
47. Novelty: 0 rejects across 231 candidates; max similarity 0.529.
48. Max similarity: 0.529 (threshold 0.60).
49. Fidelity: 233/233 evidence spans byte-exact in KB (0 mismatches).
50. generalization-cases.json sha256:
    3f22c19b9f48e748ed5b5aadd0f715430e914225fc2923edd0e953cf09e720d4.
51. Sealed-answer sha256:
    e25b3ab813274662e354d4502192c2639df765bb3e5c5e67e616cba1fa32498a.
52. Encryption/AAD: AES-256-GCM, fresh secrets.token_bytes(32) key,
    12-byte nonce; AAD = ASCII bytes of lowercase hex sha256 of the
    exact generalization-cases.json bytes; roundtrip verified before
    plaintext removal.
53. Key persisted: NO (full-repo value scan clean; key exists only in
    this session's final message).
54. Plaintext leakage: 0 (labels-final/labels-pass2/cases-pass1/
    case_list_*/adjudicate_resolve.py all removed; live only inside
    construction-audit.sealed).
55. Snapshot executed: NO (no prediction artifacts exist; construction
    scripts never imported or invoked the snapshot engine).
56. Semantic gate: PASS (construction-stage agreement gate).
57. Proof-safe gate: PASS.
58. Product gate: PASS.
59. Auto precision gate: PREREGISTERED, open until G1/G2 (>=99%).
60. Auto coverage floor: PREREGISTERED >=20% (evaluation-metrics.md).
61. Necessary-review gate: PREREGISTERED, open until G1/G2 (>=95%).
62. Unnecessary-review gate: PREREGISTERED, open until G1/G2 (<=15%).
63. Abstain gate: PREREGISTERED, open until G1/G2 (>=90%).
64. Review-vs-abstain gate: PREREGISTERED, open until G1/G2 (macro F1
    >=90%).
65. Structural-proof gate: PREREGISTERED (=0 until G1/G2).
66. Groundedness gate: PREREGISTERED (=0 until G1/G2).
67. Semantic-soundness gate: PREREGISTERED (=0 until G1/G2).
68. Proof-safe-auto gate: PREREGISTERED (=0 until G1/G2).
69. Compound atom gate: PREREGISTERED (>=90% until G1/G2).
70. Compound product gate: PREREGISTERED (>=90% until G1/G2).
71. Remaining architectural weaknesses: see "Weaknesses" below.
72. Development gates passed: all construction-stage gates (core size,
    quotas, agreement x4, adjudication cap, atom completeness, novelty,
    fidelity, seal hygiene, snapshot integrity, id guards, JSON validity,
    KB read-only; QA_FAILS=0/32).
73. Development gates failed: none. Runtime gates are open by design
    (G1/G2 is a separate phase), not failed.
74. STATUS: GENERALIZATION_HOLDOUT_SEALED_AND_READY.
75. Exact blockers: none.
76. Recommended next action: schedule G1 as a fresh keyless session per
    future-generalization-protocol.md (verify hashes, run snapshot on
    CORE once, freeze predictions, STOP), then G2 scoring with the
    preregistered policy; no tuning between or after.

## Weaknesses (item 71)

- Residual annotation disagreements concentrated in two recurring
  boundaries: temporal binding of undated rates, and scope of general
  rules vs single dated examples. The contract now codifies both, but
  they remain the likeliest scoring-interpretation friction points.
- 11 CORE cases are question-form claims; they are valid targets (the
  runtime must handle questions) but their verdicts lean on
  category-membership inference more than span matching.
- The atom pipeline's "genuine insufficiency" boundary (ABSTAIN vs
  REVIEW) is codified but was the second-largest dispute class; expect
  the same boundary to be the hardest runtime routing case.
- Reserve pool (72 cases) was quality-validated but not double-
  annotated or sealed; do not treat it as scored evidence.

## Provenance and integrity

- All historical artifacts immutable; burned-V4 shadow results
  byte-identical (verified in QA).
- GPT-5.6-Luna used for annotation pass 2 only, temperature 0, via
  local proxy; 0 of 2 subagent budget used; GPT-5.5 nowhere.
- No new NAV research; KB read-only throughout.
- A stale goal objective (kommunal psykisk helse research) was present
  in the session context; it is explicitly cancelled by TASK-LOCK and
  was not pursued.
