# RC3.3.2 ANNOTATION CONTRACT REPAIR - FINAL REPORT

Task ID: NAV-EXPLORE-RC3_3_2-ANNOTATION-CONTRACT-REPAIR

## TERMINAL STATUS

**ANNOTATION_CONTRACT_NOT_READY**

Calibration set 2 passed all reproduction gates, and the contract was
frozen. On the existing 30 micro-validation cases, the pre-adjudication
agreement gates (spec 24) did NOT all pass. Per spec 24 and 30, no
adjudication was performed, no answer key was sealed, no key exists, and
the candidate was never executed. The one allowed contract-text repair
(spec 18) is spent; no second repair is permitted.

## What was done

1. Historical integrity verified before and after work
   (integrity-start.json; integrity_check.py re-run OK):
   candidate manifest c66c14a6..., 30-case file c231979d..., large
   60-case validation 15b13bb7...; HISTORICAL_FILES_MODIFIED = 0.
2. annotation-contract-v3.md (contract) and annotation-contract-v3.schema.json
   (single shared schema) written per spec 3-15. REVIEW_REQUIRED is not in
   the semantic enum; quantity/temporal/comparator/arithmetic fields are
   structured with canonical enums and cross-field guards.
3. Calibration set 1 (CC3-001..020) built from KB spans; two independent
   GPT-5.6-Luna passes (temperature 0, fresh context per pass, schema-
   validated). quantity_identity 93.75% and comparator_relation 87.5%
   failed; the single permitted contract repair (REPAIR 1: PARTIAL
   compound claims bind quantity fields to the established conjunct,
   plus a schema guard enforcing the comparator 4-condition rule) was
   applied. Old annotations were never shown to any annotator.
4. Calibration set 2 (CD3-001..020) built as fresh development-only cases.
   Two fresh passes: semantic 95, quantity_identity 100, temporal 100,
   comparator_applicable 100, comparator_relation 100, arithmetic 100
   (all gates pass). Contract frozen: contract-freeze.json,
   status ANNOTATION_CONTRACT_V3_FROZEN.
5. The existing 30 cases were re-annotated byte-identically
   (SHA c231979d... verified) in two fresh passes. Both passes: 30/30
   completed, schema_failures = 0.

## 30-case pre-adjudication agreement (final-agreement.json)

| Field | Agreement | Gate | Result |
|---|---|---|---|
| semantic_relation | 96.67% | >=90% | PASS |
| quantity_identity | 94.74% | >=95% | FAIL |
| temporal_applicability | 100% | >=90% | PASS |
| comparator_applicable | 90.0% | >=95% | FAIL |
| comparator_relation | 66.67% (union denominator; 88.9% on both-applicable) | >=95% | FAIL |
| arithmetic_duty | 96.67% | >=95% | PASS |

Schema failures on final passes: 0. Dispute cases: RC33M2-001, 003, 004,
006, 010, 011, 019, 024, 026 (9 cases touched at least one field).

## Root causes of residual disagreement (not memorized case mappings)

1. Comparator-necessity interpretation on exact-match entailments.
   Cases 001/024/006: one pass treats comparator fields as NOT_APPLICABLE
   when claim and source state the same quantity, the other applies the
   4-condition rule (condition 3: "comparator-forholdet er nodvendig")
   and reaches EQUIVALENT/SOURCE_STRONGER. The rule admits both readings;
   the contract freezes a definition but not a decision procedure for
   "necessary for the relation".
2. quantity_value_source under aggregation and period extension.
   Cases 003 (sum), 011 (baseline 3 months inside a 6-month extended
   window): role AGGREGATE / DERIVED leaves the source value ambiguous,
   and both passes disagreed 5 times on this field.
3. Deictic temporal anchors. Case 004 ("denne uken"): one pass bound the
   anchor and stayed PARTIAL; the other left quantity identity unresolved
   and answered AMBIGUOUS. The temporal contract lacks a rule for
   anchoring relative time expressions.

These are contract-clarity problems, not annotator-format problems: zero
schema failures, 100% role agreement, 100% temporal-enum agreement among
applicable pairs.

## Boundaries and non-claims

- Adjudication: NOT performed (gates failed).
- Answer key: NOT sealed; no key material exists anywhere on disk.
- Candidate execution: 0 cases; candidate context never saw case content.
- Large 60-case validation: untouched (SHA re-verified after work).
- Old annotations: remained quarantined; no annotator input included them.
- The repair budget is exhausted; a second repair would violate spec 18.

## Recommended next step (future task, not this one)

The failures are concentrated and fixable by contract text: (a) freeze a
deterministic comparator-necessity rule for exact-match cases, (b) freeze
quantity_value_source semantics for AGGREGATE/DERIVED roles and extended
periods, (c) freeze a rule for deictic temporal anchors. A new task must
draft these as contract v4, re-calibrate with two fresh 20-case sets, and
only then re-run the 30 cases. This task is closed without a sealed key.
