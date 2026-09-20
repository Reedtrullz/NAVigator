# Final report - SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR

All 58 SLUTTRAPPORT points. Verified state: 2026-09-03, after the single
implementation pass and full QA battery.

1. **Task lock**: SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR (TASK-LOCK.json,
   status ACTIVE during work). Forbidden tasks not performed: Tier-2, new
   proof operators, new inference doctrine, reviewer tuning, packet R&D,
   holdout-v3, blind recert, live dialog, NAV/kommune research, KB tuning.
2. **Known coverage gaps**: 7 (known-coverage-gaps.json; exactly 7).
3. **Solvable with existing proof-path**: 3 (CAL011, CAL014, CAL034).
4. **FALSE_SHOULD_AUTO_CLASSIFICATION**: 0. All seven proofs were
   constructible from existing evidence; the four remaining gaps are
   doctrine boundaries, not annotation errors.
5. **Bug taxonomy**: bug-taxonomy.md. Classes used: LEXER_MISS (2),
   LEXICON_ALIAS_MISS (3 primary), NUMERIC_BINDING_BUG (1),
   PIPELINE_PLUMBING_BUG (1), plus secondary NEGATION_BINDING_BUG,
   TEMPORAL_BINDING_BUG, ACTOR_TYPE_MISS, SPAN_SELECTION_BUG,
   OPERATOR_ELIGIBILITY_BUG, PROOF_VALIDATOR_BUG.
6. **Lexer bugs**: standalone "G" not a unit; "g" pattern without word
   boundary collided with "ganger"; space-formatted thousands separator
   ("6 385") still unlexed (HOL014, not fixed - see 52).
7. **Lexicon bugs**: "ingen henvisning"/"ingen kostnad" negative forms
   missing or shadowed by positive heads; no voluntariness concept
   (MOD-14, not fixed - new rescue doctrine).
8. **Actor bugs**: dummy subject "Det er ..." has no lexical actor
   (relaxed for exclusion-cutoff claims only); multiword actor equality
   ("BUP i Trondheim") blocked by a load-bearing hybrid guard (LOC-13,
   not fixed).
9. **Predicate/normalization bugs**: none new; longest-match-first
   polarity normalization repaired ("ingen kostnad" as free-of-charge).
10. **Qualifier/negation bugs**: double-negative forms lexed by LMF;
    exclusion thresholds ("ingen ... over X") now bound-conflict.
11. **Plumbing/operator-eligibility bugs**: numeric operator required
    same-subject binding for subjectless claims and single-bound
    conflicts for mixed conjuncts; fragment chaining missing between
    operator and validator; validator re-derivation had drifted from
    operator semantics (both now share _conflicting_pair).
12. **Implemented general fixes**: F1-F9 in coverage-fix-spec.md (LMF
    polarity, G-unit + word boundary, framing extension, "ingen
    henvisning" form, fragment chaining, dummy-subject relaxation,
    exclusion-threshold conflict, mixed-conjunct pre-pass, validator
    alignment). All general; none case-specific.
13. **Files/lines changed**: implementation-report.md. 4 runtime files,
    2 test files, ~110 lines added, ~25 reworked.
14. **Near-miss tests**: yes, per fix (spec 13): unit tests 43/43 and
    permanent regression cases NUM-THRESH-SAME/UNIT, NUM-GWORD,
    NUM-MIXED-CONJ, DA-FRAG-ORPHAN (operator regression 23/23).
15. **Case CAL011**: FIXED_SAFE_AUTO - DIRECT_ASSERTION, premise S2
    ("Gratis, ingen henvisning."), chained to bound S1; auto-SUPPORTED.
16. **Case CAL014**: FIXED_SAFE_AUTO - DIRECT_ASSERTION, premise S3
    ("Ingen henvisning, ingen aldersgrense ..., ingen kostnad."); auto-
    SUPPORTED.
17. **Case CAL034**: FIXED_SAFE_AUTO - NUMERIC_CONFLICT, premise S2, 4 G
    vs 6 G exclusion thresholds; auto-CONTRADICTED.
18. **Case HOL006**: REMAINS_REVIEW_BY_DESIGN - multiplier ("ganger
    grunnbeloepet") conflict needs a compound numeric gate = new
    doctrine; spec 18 accepts review.
19. **Case HOL014**: REMAINS_REVIEW_BY_DESIGN - space-formatted
    thousands separator unlexed AND unknown-time-axis comparability
    (strict time rule); relaxing the time rule is a doctrine change.
20. **Case LOC-13**: REMAINS_REVIEW_BY_DESIGN - engine already
    SUPPORTED; hybrid numeric_support_binding multiword-actor guard is
    load-bearing (also gates CAL021/CAL023 misfires).
21. **Case MOD-14**: REMAINS_REVIEW_BY_DESIGN - near-verbatim support
    would need a voluntariness concept plus dummy-subject-to-noun chain
    = new rescue doctrine.
22. **FIXED_SAFE_AUTO count**: 3.
23. **REMAINS_REVIEW_BY_DESIGN count**: 4.
24. **IMPLEMENTATION_BUG_NOT_FIXED count**: 0.
25. **Auto decisions before**: 121 (of 389).
26. **Auto decisions after**: 122 (net: +4 review-to-auto, -3 unsafe
    auto retracted).
27. **Review finals before**: 27.
28. **Review finals after**: 27 (net zero: 4 in, 4 out).
29. **Necessary reviews after**: 1 (unchanged).
30. **Unnecessary reviews after**: 5 (unchanged; Tier-2 candidates
    MP-015A, N-S5, N-L2, N-L3, N-O3).
31. **Invalid accepted proofs**: 0 (baseline had 3 auto rows with
    proof_safe=INSUFFICIENT: N-A4, N-R1, ENT-C - all retracted).
32. **Unsafe auto-SUPPORTED**: 0.
33. **Unsafe auto-CONTRADICTED**: 0.
34. **Product decision correctness**: 4 new correct auto decisions
    (ACT-25, CAL011, CAL014, CAL034), 0 false auto decisions, 0
    conflicts; dual-row semantic accuracy unchanged at 45/80 (the
    converted rows are review-path rows without dual labels; the 3
    retracted rows move to correct safe review).
35. **ENT-A**: INSUFFICIENT -> INSUFFICIENT (unchanged, safe).
36. **ENT-B**: INSUFFICIENT -> INSUFFICIENT (unchanged, safe).
37. **ENT-C**: was invalid auto-CONTRADICTED; now retracted to
    REVIEW_REQUIRED with no proof - canary intact (hard requirement).
38. **ENT-D**: CONTRADICTED -> CONTRADICTED (unchanged).
39. **ACT-25**: auto-SUPPORTED via valid DIRECT_ASSERTION (premise S1)
    - positive reference intact.
40. **N-A4**: retracted to review (safe).
41. **N-R1**: retracted to review (safe).
42. **Operator regression**: 23/23 PASS (16 existing + 7 new).
43. **Quote-aligner regression**: REGRESSIONS: 0; 7 documented
    residuals unchanged. Determinism: 5 runs x 225 cases identical.
44. **Evaluator regression**: accuracy 1.00, precision 1.00, recall
    1.00, safety_FP 0 (TP 24, TN 96, FP 0, FN 0).
45. **KB regression**: Total 48, BESTATT 48, DELVIS 0, FEILET 0.
46. **id_guard**: 0 violations.
47. **qa_check.sh**: OK ("ingen kjente feilmnstre funnet"), exit 0.
48. **RC1 created**: yes - evaluation/semantic-judge/release-candidate/
    (RC1-manifest.json, hashes.txt, readiness-report.md).
49. **RC1 manifest/hash verification**: 17 runtime/contract files
    SHA-256 hashed post-QA; manifest lists component versions; hashes
    recorded after the last test run so they reflect the frozen bytes.
50. **Evaluation-contract version in RC1**: evaluation contract as
    frozen by contract-freeze-manifest-v1 (2026-09-02, SEMANTIC-JUDGE-
    TIER1-PROOF-OPERATORS); contract files hashed in RC1 manifest.
51. **Runtime components in RC1**: quote-aligner v0.2 (+ frozen v0.1
    engine), Tier-1 operators (tier1-proof, this pass's fixes), hybrid
    reviewer v1.1 + auto_gate v0.1 + fusion (frozen spec), semantic
    judge v0.4.1, evaluation contract (frozen). Full list with hashes
    in RC1-manifest.json.
52. **Remaining known bugs**: HOL014 thousands-separator lexing (safe
    to fix in a future doctrine-bounded pass together with its
    time-compatibility companion), LOC-13 multiword-actor guard
    (deliberate), MOD-14 voluntariness concept (rescue doctrine),
    HOL006 multiplier axis (compound numeric gate), CAL010-style
    baseline-SUPPORTED rows gated by hybrid guard (legitimate).
53. **Remaining necessary reviews**: 1 (dual-labelled, appropriate).
54. **Tier-2 still SKIP**: yes - SKIP_TIER2 stands; the 5 unnecessary
    reviews are Tier-2 candidates and stay untouched.
55. **Readiness**: READY_TO_BUILD_BLIND_RECERTIFICATION_SET - invalid
    accepted proofs 0, critical auto errors 0, current-contract
    regressions pass, operator regression pass, KB 48/48, evaluator
    regression clean, id_guard 0, qa_check PASS, freeze manifest
    complete (spec 27).
56. **Runtime frozen**: yes - RC1 hashes recorded; no tuning before
    blind recertification results exist (spec 26). Any further change
    requires RC2, never an RC1 edit.
57. **If NOT READY blocker**: n/a (READY).
58. **Recommended next step**: build the blind recertification set as a
    separate task (SEPARATE annotation agent/process, spec 29-31):
    annotate semantic truth, proof-safe verdict, product expected
    action, required inference/operator, annotation status; then test
    the exact RC1 hashes. Do not reuse v0.1/v0.2 holdout items; do not
    modify RC1.

## Per-spec QA notes

- Spec 16 (all 30 review finals): re-run after the pass - 27 baseline
  REVIEW rows re-evaluated by the gate; 3 moved to auto (CAL011,
  CAL014, CAL034), ACT-25 re-confirmed; remaining reviews match
  doctrine (necessary 1, unnecessary 5, the latter Tier-2 candidates).
- Spec 30 (future blind-set contract): confirmed in point 58; no cases
  built.
- Spec 32 (KB issues): none discovered that would warrant
  POTENTIAL_KB_ISSUE flags; no KB edits made.
