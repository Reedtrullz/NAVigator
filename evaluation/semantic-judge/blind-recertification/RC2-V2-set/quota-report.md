# Quota report - RC2 blind set V2 construction

Instrument: the task's own quota_check.py targets, evaluated over the retained pool (n = 277, all quotas pass). Per-case authoring meta was plaintext-scrubbed after sealing (spec 44), so pool flag counts below are the construction-session verified snapshot (DB snapshot exec-9ba70a3c / exec-b157f072 provenance, recorded in blind-manifest.json).

## Pool-wide quota results (n = 277, ALL_QUOTAS_PASS)

| Quota | Target | Pool count | Result |
|---|---|---|---|
| Total candidates | >= 220 | 277 | PASS |
| semantic SUPPORTED | >= 40 | 133 | PASS |
| semantic CONTRADICTED | >= 40 | 64 | PASS |
| semantic PARTIALLY_SUPPORTED | >= 40 | 40 | PASS |
| semantic INSUFFICIENT_EVIDENCE | >= 40 pool / min 30 | 40 | PASS |
| product AUTO_SUPPORTED | >= 25 | 132 | PASS |
| product AUTO_CONTRADICTED | >= 25 | 64 | PASS |
| product REVIEW_REQUIRED | >= 25 | 41 | PASS |
| product ABSTAIN_INSUFFICIENT | >= 25 | 40 | PASS |
| compound | >= 50 | 50 (51 in final pool incl. RC2B-0277) | PASS |
| multi_span | >= 30 | 44 | PASS |
| numeric | >= 30 | 128 | PASS |
| age/legal-reference | >= 20 | 42 | PASS |
| temporal | >= 30 | 56 | PASS |
| actor/role | >= 30 | 100 | PASS |
| modality | >= 30 | 138 | PASS |
| safety-critical | >= 20 | 20 | PASS |
| legal/rights | >= 30 | 109 | PASS |
| locality Trondheim | >= 20 | 46 (+1 = 47 with RC2B-0277) | PASS |
| condition/exception required | >= 30 | 41 | PASS |

## CORE-level deviations (documented, not silently patched)

1. Genuine insufficiency: the spec 12 minimum is 30 genuine INSUFFICIENT among CORE. All 40 genuine INSUFFICIENT cases were authored and retained pool-wide, but the firewall CORE selection placed all of them in reserve; CORE contains 0. CORE semantic distribution: SUPPORTED 94, CONTRADICTED 41, PARTIALLY_SUPPORTED 25, INSUFFICIENT_EVIDENCE 0. Post-seal label or selection edits are forbidden (spec 48), so this is documented as a set-design deviation; a strict-gate rebuild would be a V3.
2. Multi-span: the spec 17 minimum is 30 CORE cases requiring at least two evidence spans. The authoring design flagged 44 multi-span cases pool-wide, but only 18 CORE cases expose two or more spans in the final public packets (the sealed answer keys for the remainder resolve to a single primary span). Documented as a deviation for the same reason.

Both deviations are recorded in blind-manifest.json core_deviation_notes and in final-report.md.
