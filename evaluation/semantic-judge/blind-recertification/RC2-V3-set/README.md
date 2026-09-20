# RC2 blind recertification set V3 - NAV-EXPLORE-RC2-BLIND-V3

Sealed double-annotated blind set for RC2 evaluator certification. RC2 has never been executed against these cases (manifest rc2_executed_on_blind_set: false).

## Artifact map

| File | Purpose |
|---|---|
| blind-cases.json | Public, label-free CORE cases (160). SHA-256 ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d |
| blind-cases.schema.json | Draft-07 schema for the public case shape (incl. provenance) |
| answer-key.sealed | AES-256-GCM sealed answer key covering all 160 CORE cases (final triple, flags, pass1/pass2, adjudication status, provenance, primary_kb, rationale/atoms for adjudicated cases). SHA-256 45323257f325cca82bc80167ff09cda4da1d93ff441445fcd604cfbb71e2aeb9. Envelope associated_data is urlsafe-b64 of the raw blind-cases SHA-256 digest; the AES-GCM AAD bytes are the UTF-8 hex string |
| blind-manifest.json | Machine-readable construction manifest: distributions, flags, agreement, fidelity, novelty, hash verification |
| selection.json | Case-ID selection (core/reserve) plus counts. No per-case labels |
| annotation-contract-v3.md, annotation-flags-v3.md | Certified annotation contract (pilot round 3) |
| annotation-pilot-report.md | 32-case pilot, rounds 1-3 audit trail, gate PASS |
| annotation-summary.md | Two-pass agreement aggregates and all 23 adjudications with rationales |
| selection-report.md | Constraint-based CORE selection (spec 22-24), zero failures |
| quota-report.md | CORE-only quota verification (spec 19-21), zero failures |
| novelty-report.md | Novelty gate (282/282 retained, max similarity 0.5385) |
| source-fidelity-report.md | Verbatim-excerpt fidelity (282/282, 0 failures) |
| certification-metrics.md | Pre-registered gates and thresholds, fixed before any RC2 run |
| future-certification-protocol.md | Two-phase prediction-freeze firewall incl. key-handling rules |
| construction-qa-report.md | Fail-closed CORE-only QA results and regression-test evidence |
| final-report.md | SLUTTRAPPORT (items 1-57) |
| construction/ | Construction working files: candidate waves, pass1/pass2 outputs, pool-annotated.json (labels), selection tooling, seal script, per-check reports |
| qa-tests/test_construction_qa.py | Permanent regression tests for the V2 construction bug (spec 43) |
| TASK-LOCK.json | Task lock |
| v2-selection-qa-root-cause.md | V2 postmortem: why QA said ALL_QUOTAS_PASS (spec 3-4) |

## Label-bearing construction files

construction/pool-annotated.json, pass1-locke.json, pass2-hypatia.json, both gap-wave pass files, disputes.json and adjudicate.py (embedded FINAL rationales) contain plaintext labels and are retained inside construction/ as construction evidence. Spec 36 leak scanning was applied to the public blind artifacts (candidates, blind-cases, selection, annotation inputs), matching the V2 qa_check.sh precedent; the sealed answer key is the canonical label source for certification. construction/seal_key.py is retained for provenance but regenerating requires the construction inputs and yields a NEW key - it must never be run against the sealed set.

## Certification firewall

The key was delivered once, in the construction final message, memory-only. It is not stored on disk, in the repo, in Obsidian, or in any report. Certification runs follow future-certification-protocol.md: Phase 1 is keyless (predictions frozen before any labels exist in the run context), Phase 2 scores only after the user supplies the key.
