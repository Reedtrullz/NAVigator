# Security Report - Certification

Task: NAV-EXPLORE-LOCAL-DISCOVERY-V2_3-CANDIDATE-CERTIFICATION
Date: 2026-09-09

## Credential handling

- EXTERNAL_CREDENTIAL_REQUIRED = FALSE: the frozen V2.3 runtime constructs
  no Brave/Tavily provider; certification ran without any credential.
- `scrub_credentials()` ran at the start of every certification process
  (replay, test sweep, live re-run). Presence-only policy: key names may be
  observed, values are never read, printed, or persisted. `.env.local` was
  never opened by any certification process.
- No secret value appears in any certification artifact, probe record, log,
  or this report.

## Network controls

- Probe set was bounded to burned Raelingen authoritative hosts
  (bedreinnsats.no variants, ralingen.kommune.no variants, raelingen
  kommune.no variants). No fresh municipality, no third-party search host,
  no new provider.
- external_search_calls = 0 across certification (see network-call-audit.json).
- The live re-run executes the frozen runtime unchanged, including
  validate_url SSRF rules and bounded render fallback (max 4 renders,
  45 s timeout, process-group kill).

## Security regression

- Frozen security suite passes unchanged as part of the 130/130 test sweep
  (tests_v21 SSRF/secret-safety; tests_v23 code-hygiene, localhost and
  private-IP fetch blocks).
- No security rule was added, removed, or weakened in this task.
- No runtime source file changed during certification (candidate manifest
  SHA re-verified at close: see candidate-certification.json).

## Findings

No security finding. The certification-blocking defect (Section 14) is an
availability/implementation issue, not a security issue.
