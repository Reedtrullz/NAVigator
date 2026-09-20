# RC3.3.2 Annotation Contract Repair

Task: NAV-EXPLORE-RC3_3_2-ANNOTATION-CONTRACT-REPAIR

## Terminal status

**ANNOTATION_CONTRACT_NOT_READY**

The contract was repaired once, calibrated successfully on a fresh 20-case
set, and frozen. Re-annotation of the existing 30 micro-validation cases
completed twice with zero schema failures, but the spec-24 pre-adjudication
agreement gates did not all pass (quantity_identity 94.74% < 95%,
comparator_applicable 90% < 95%, comparator_relation 66.67% < 95%). Per
spec, adjudication was not allowed, no answer key exists, and the candidate
was never executed.

## Contents

- annotation-contract-v3.md / annotation-contract-v3.schema.json - frozen
  canonical field contract and shared JSON schema (SHA in contract-freeze.json)
- contract-calibration-set-1.json / calibration-results-1.json - round 1
  (two gate failures triggered the single allowed repair)
- contract-calibration-set-2.json / calibration-results-2.json - round 2
  fresh cases, all gates pass
- contract-freeze.json - ANNOTATION_CONTRACT_V3_FROZEN with hashes
- pass1-results.json / pass2-results.json - fresh 30-case annotations
- final-agreement.json - the failing gate computation
- agreement-report.md, annotation-summary.md, historical-integrity.md,
  final-report.md - reports
- integrity-start.json - pre-work integrity snapshot

## Rules honored

Historical files unmodified (HISTORICAL_FILES_MODIFIED=0); candidate
unexecuted; large 60-case validation untouched; old annotations quarantined;
GPT-5.5 never used; no key material ever created.
