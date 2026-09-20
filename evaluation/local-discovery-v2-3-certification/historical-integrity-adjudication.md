# Historical Integrity Adjudication

Task: NAV-EXPLORE-LOCAL-DISCOVERY-V2_3-CANDIDATE-CERTIFICATION
Date: 2026-09-09

## Incident (permanent record)

HISTORICAL_WRITE_INCIDENT = TRUE.

During the V2.3 task, `runtime/discovery_v2/providers.py` was transiently
modified (a `max_urls` edit). The event was disclosed in the V2.3
implementation report at the time. Per certification contract Section 4,
this remains permanently registered; it is not erased by restoration.

## Restoration verification (current byte integrity)

Authoritative baseline: V2.1 implementation snapshot
(`evaluation/local-discovery-provider-v2-1/implementation-snapshot/manifest.json`),
entry `runtime/discovery_v2/providers.py`.

- Expected SHA-256: `54b38921b02736763d3baef25e7bb860f1bf1b9f8d3b0fb3ac58b0808083806a`
- Current SHA-256: identical. The historical file is byte-identical to the
  authoritative V2 baseline.
- Full V2.1 snapshot cross-check: 7/7 files listed in the snapshot manifest
  that exist on disk match their frozen SHAs (0 mismatches).
- Unknown residual differences: none found by SHA cross-check of the
  snapshot set and the 19-file candidate manifest.

## Lineage isolation (Section 6)

- V2.3 URL budget (16) is owned solely by `SiteDirectProviderV23`, a
  subclass defined in `runtime/discovery_v2/cli_v23.py`; the historical
  `SiteDirectProvider` retains the frozen default (8) and contains no V2.3
  or budget-override references (grep: 0 hits for `max_urls`/`V23` in
  `runtime/discovery_v2/providers.py`).
- The frozen provider config documents this separation explicitly.
- The V2.3 candidate therefore does not depend on any modified historical
  V2 file; the restored file is the same frozen implementation the V2.1
  task froze.

## Integrity adjudication (Section 7)

**RESTORED_WITHOUT_CANDIDATE_CONTAMINATION**

Byte-identical restoration plus new-lineage ownership of all V2.3 behavior
supports this status. The write incident itself remains a registered
protocol deviation and is reported as such in the certification record.

## Distinction required by Section 30

- Current byte integrity: PASS (today, verified from disk).
- Historical write incidents: TRUE (occurred, disclosed, restoration
  verified). Reporting `historical_files_modified = 0` today would be true
  for this certification task but must never be used to deny the incident.

## Harness incident (Section 18)

EVALUATION_HARNESS_INCIDENT = TRUE. The initial V2.3 replay attempt
returned 0/22 because the runner routed replay cells through the site-direct
provider against anchor-less fixture pages. Root cause was isolated to the
evaluation harness: replay was re-wired to frozen V1 search-index semantics
(matching the pipeline that produced the historical rerun predictions), the
candidate runtime was unchanged, and the corrected run reproduced 22/22.
The clean certification re-run (Section 19) also produced 22/22 from a fresh
process.
