# FINAL REPORT - V1.6A.2 ROUTE-GROUNDING REPAIR

## 1. Task ID
NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A2-ROUTE-GROUNDING-REPAIR

## 2. Prior status
V1.6A.1 boundary pre-classifier frozen (SHA 40d85f317383...de768d);
ADV-11 cross-clause operator leak identified as root cause; this task
implemented clause-locality repair in a new lineage.

## 3. V1.6A integrity
All V1.6A artifacts SHA-verified in baseline-integrity.json. No historical
writes (historical_writes = 0).

## 4. V1.6A.1 integrity
All V1.6A.1 artifacts SHA-verified in baseline-integrity.json. No historical
writes (historical_writes = 0).

## 5. Historical writes
0

## 6. ADV-11 classified diagnostic-only?
YES. Used only for root-cause trace and mechanism abstraction. Never used as
regression anchor or exact-match target.

## 7. Previous targeted-60 marked burned?
YES. BURNED_DIAGNOSTIC_DATA per V1.6A.1 process deviation (recorded
permanently in process-deviations.md).

## 8. Section 20 deviation preserved?
YES. process-deviations.md carries the permanent V1.6A.1 TDD_SEQUENCE_DEVIATION
record plus the new DEV-02 bounded bugfix pass record for this task.

## 9. Root cause reproduced?
YES. ADV-11 (CROSS_CLAUSE_OPERATOR_LEAK) reproduced on frozen V1.6A.1 engine:
assertion in clause 0 fired output-wide ASSERTED while unknown noun in clause 1
was never evaluated. Reproduction documented in root-cause-trace.json.

## 10. Fired historical rule
BC_ROUTE_ASSERTED_01 (V1.6A.1, ADV-11)

## 11. Clause-level trace
Engine guard skipped noun scan entirely when any inventory term existed;
assertion operator had no clause-locality check. Clause 0 (inventory noun +
assertion) dominated clause 1 (unknown noun, no operator). Full trace in
root-cause-trace.json.

## 12. Frozen generalized hypothesis
Clause-level route grounding: every route candidate must be grounded by a
licensing operator (assertion, hedge, negation, retraction, quote, conditional)
within the same clause; ungrounded candidates -> ABSTAIN. Mixed commitment
strengths across clauses -> ABSTAIN. Frozen pre-implementation in
repair-hypothesis.md.

## 13. Case-specific logic? MUST NO
NO. No case IDs in runtime. No literal case-to-verdict mappings.

## 14. Clause locality implemented?
YES. BC_ROUTE_CLAUSE_LOCALITY_01: ungrounded candidate -> ABSTAIN.

## 15. Negation locality
YES. Negation binds only within the same clause as its target noun.

## 16. Retraction locality
YES. Retraction binds to inventory candidates; correction binding allows clause
ci+1 retraction to retroactively ground clause ci (VR-R-01..04 / CMT-R-04).

## 17. Quote locality
PARTIAL. Quote spans suppress assertion markers inside guillemets.
BC_ROUTE_QUOTE_CONFLICT_01 fires when quote + external assertion coexist.
Fresh-set execution revealed residual gap: bare-quote-only output emits
QUOTED_ONLY deterministically; bare-quote ABSTAIN is not implemented (matches
burned V1.6A precedent VR-Q-04; gap vs stricter fresh gold). Not patched
post-execution.

## 18. Hedge locality
PARTIAL. Hedge binds within its clause. Fresh-set execution revealed residual
gap: two hedged clauses with different nouns produce a single HEDGED_ASSERTION
when both are inventory terms. Not patched post-execution.

## 19. Ambiguous grounding -> ABSTAIN?
YES for 2+ candidates sharing one clause (BC_ROUTE_AMBIGUOUS_02, except
conditional frame). Cross-clause two-candidate competition is handled by mixed
polarity guard only when 2+ candidates exist; single-candidate cross-clause
mixed polarity remains a gap (OFF-SCOPE-05, OFF-SCOPE-17).

## 20. New TDD fixtures N
17 (16 original + TDD-CROSS-07 added post-burned-freeze as contract-derived RED)

## 21. Genuine RED?
YES. TDD-CROSS-07 failed on pre-fix engine (16/17 pass; the new fixture failed).
RED result preserved in tdd-red-result.json.

## 22. Existing tests N
72 (V1.6A.1 unit suite carried forward)

## 23. New tests N
1 (TDD-CROSS-07)

## 24. Total GREEN
TDD 17/17, unit 72/72, burned-120 all gates PASS, burned-60 precision 1.0

## 25. Burned-120 overall precision
1.0 (108 non-abstain, 0 false deterministics)

## 26. Burned-120 route precision
1.0

## 27. Burned-120 false deterministic
0

## 28. VR-H-08 result
ABSTAIN (correct; V1.6A.1 out-of-inventory rule preserved)

## 29. Burned-targeted60 precision
1.0 (29 non-abstain, 31 abstain, 0 false deterministics)

## 30. ADV-11 diagnostic result
ABSTAIN via BC_ROUTE_CLAUSE_LOCALITY_01 (correct; historical label was ASSERTED).
Root cause repaired.

## 31. Engine frozen before fresh set?
YES (post-bugfix SHA 21637fdfcc8e6883... recorded in official-fixture-hashes.json;
fixtures frozen before official run).

## 32. Fresh official fixtures N
80 (batch 1: 40 group A+B; batch 2: 40 group C+D)

## 33. Engine queries during fixture authoring - MUST 0
0 (authoring_engine_queries = 0)

## 34. Disputed fixtures removed N
0 (no disputes during authoring)

## 35. Disputed fixtures retained - MUST 0
0

## 36. Annotation provenance
INTRA_ANNOTATOR_REPEATABILITY (dual-pass single curator, contract section 30)

## 37. Fixture SHA
feaab60c6823218b... (full SHA in official-fixture-hashes.json)

## 38. Gold SHA
38ec77336233acfca113a1d0e71297d0d46fbb7cd599c6f14c0c0350628e054b

## 39. Official non-ABSTAIN N
37 (of 80; abstain_n = 43)

## 40. Overall precision
0.7027 (26 correct of 37 non-abstain; 11 false deterministics)

## 41. Route precision
0.7027 (same denominator; all fixtures are route_commitment dimension)

## 42. Same-clause precision (group A)
0.9412 (1 false deterministic OFF-SAME-17)

## 43. Cross-clause precision (group B)
1.0 (20/20 non-abstain correct; 0 false deterministics)

## 44. Quote/hypothetical precision (group C)
0.1818 (2/11 non-abstain correct; 9 false deterministics; 9 abstains)

## 45. Adversarial precision (group D)
0.8 (1 false deterministic OFF-ADV-12; 3 abstains)

## 46. Clause-grounding false deterministic N
0 (group B cross-clause: 20/20 correct)

## 47. Out-of-inventory false deterministic N
0

## 48. Safety false deterministic N
0

## 49. Evidence-span validity
1.0 (37/37 non-abstain spans valid)

## 50. Overall coverage
0.4625 (37/80 non-abstain)

## 51. Cross-clause coverage
1.0 (20/20 non-abstain in group B)

## 51b. Subgroup coverage (raw N mandatory, diagnostic only)

| Group | Non-abstain N | Abstain N | Total N |
|-------|---------------|-----------|---------|
| A_same_clause | 19 | 1 | 20 |
| B_cross_clause | 20 | 0 | 20 |
| C_scope | 11 | 9 | 20 |
| D_adversarial | 17 | 3 | 20 |

## 52. Error taxonomy
Error classification per contract section 36 (no patch in this task after
official start):

- CONFLICT_NOT_ABSTAINED: OFF-SCOPE-01, OFF-SCOPE-02, OFF-SCOPE-05,
  OFF-SCOPE-17 (quote/hedge/assertion + competing commitment in a separate
  clause -> engine emits a deterministic label instead of ABSTAIN)
- QUOTE_SCOPE: OFF-SCOPE-04 (parenthetical-only -> ASSERTED), OFF-SCOPE-16
  (bare quote -> QUOTED_ONLY; boundary vs ABSTAIN unresolved, engine matches
  burned precedent VR-Q-04)
- HEDGE_SCOPE: OFF-SCOPE-19 (two hedged clauses, different nouns -> single
  HEDGED_ASSERTION)
- NEGATION_SCOPE: OFF-ADV-12 (negation inside conditional antecedent ->
  NEGATED instead of HYPOTHETICAL_ONLY)

Gold-curation boundary disagreements (4, not engine regressions):
OFF-SAME-17 (gold SELF_RETRACTED but the construction never positively commits;
NEGATED is contract-consistent), OFF-SCOPE-08 + OFF-SCOPE-16 (engine
QUOTED_ONLY matches burned precedent VR-Q-04; fresh gold demanded ABSTAIN),
OFF-SCOPE-09 (trailing "dersom" qualifier; engine HYPOTHETICAL_ONLY vs fresh
gold ASSERTED; no burned precedent).

Gold-curation boundary disagreements (4, not engine regressions): OFF-SAME-17 (gold SELF_RETRACTED but "kan ikke sta inne for" never commits; NEGATED is contract-consistent); OFF-SCOPE-08 + OFF-SCOPE-16 (engine QUOTED_ONLY matches burned precedent VR-Q-04; fresh gold demanded ABSTAIN); OFF-SCOPE-09 (trailing "dersom" qualifier; engine HYPOTHETICAL_ONLY vs fresh gold ASSERTED; no burned precedent).

## 53. Candidate frozen?
NO. Gate failure blocks candidate freeze (contract section 49 stop condition).

## 54. Candidate manifest SHA
N/A (no candidate frozen)

## 55. V1.4 diagnostic replay performed?
NO (requires candidate freeze; gate failure stops before this step)

## 56. Historical misses boundary-resolved
ADV-11 cross-clause operator leak: RESOLVED by clause-locality rule (burned-60
precision 1.0, ADV-11 abstains).

## 57. Historical misses remaining
Clause-level grounding works for burned 60 and fresh group B, but fresh group
C/D expose new boundary gaps (quote scope, parenthetical scope, single-candidate
mixed polarity, hedge competition, negation-in-antecedent) that the
clause-locality abstraction does not yet cover.

## 58. Estimated judge-call reduction
Burned-120: 25% (30/120 abstain). Official-80: 54% (43/80 abstain). Both
estimates are unreliable until precision is repaired; a 0.70-precision engine
cannot be deployed for judge-call reduction regardless of coverage.

## 59. Semantic judge evaluation calls - MUST 0
0

## 60. V1.6B run - MUST NO
NO

## 61. Product runtime changed - MUST NO
NO

## 62. Gates passed
Full suite green (TDD 17/17, unit 72/72); burned-120 all gates PASS; burned-60
precision 1.0 + ADV-11 correct; fixture authoring 0 engine queries; text-reuse 0
across all burned sets; fixture/gold hashes frozen; gold QA 80/80;
clause-grounding false deterministic 0; out-of-inventory false deterministic 0;
safety false deterministic 0; evidence-span validity 100%.

## 63. Gates failed
Overall non-ABSTAIN precision 0.7027 < 0.99; group C precision 0.1818 < 0.98;
group A precision 0.9412 < 0.98; group D precision 0.8 < 0.98; total false
deterministic 11 > 0.

## 64. STATUS
V1_6A2_FRESH_CONFIRMATION_NOT_READY

## 65. Is V1.6B now justified?
NO. V1.6A.2 did not reach READY; V1.6B remains blocked.

## 66. Recommended next bounded stage
Contract-derived engine repair targeting the 7 genuine gaps:
1. Quote scope: bare quote + no external commitment -> ABSTAIN (vs attributed
   quote -> QUOTED_ONLY precedent); parenthetical-only -> ABSTAIN.
2. Single-candidate cross-clause mixed polarity -> ABSTAIN (extend mixed guard).
3. Hedge competition: 2+ hedged clauses with different nouns -> ABSTAIN.
4. Negation inside conditional antecedent: does not promote to NEGATED.
5. Resolve QUOTED_ONLY vs ABSTAIN boundary with explicit contract clarification
   (attributed vs bare quote) before regenerating fresh fixtures.
Then: freeze -> fresh official 80 -> one-shot -> gate evaluation. One bounded
implementation pass per contract section 49.
