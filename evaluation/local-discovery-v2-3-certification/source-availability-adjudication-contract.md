# Source-Availability Adjudication Contract (frozen before any new live probe)

Task: NAV-EXPLORE-LOCAL-DISCOVERY-V2_3-CANDIDATE-CERTIFICATION
Frozen: 2026-09-09, before the first certification probe (Section 9).

This contract classifies observations. It never changes the frozen V2.3
runtime, config, or benchmark score.

## Classes

### RUNTIME_INTERNAL_FAILURE
The runtime/provider implementation itself failed: unhandled exception,
budget exhaustion on a reachable host, wrong-host construction, or any
defect that made the runtime probe a source other than the relevant one.

### SOURCE_HTTP_UNAVAILABLE
The public source cannot be fetched: HTTP >= 400, connection refused or
reset, TLS failure, or timeout beyond the frozen runtime budget (15 s per
fetch, no retries).

### SOURCE_RENDER_UNAVAILABLE
The source requires rendering that the frozen runtime capability
(headless Chrome, virtual time budget 12000 ms, timeout 45 s, max 4
renders per municipality) cannot achieve: empty DOM dump or timeout on a
host that is otherwise up.

### SOURCE_DNS_UNAVAILABLE
The authoritative host cannot be resolved by the OS resolver.

### SOURCE_CONTENT_UNUSABLE
The host answers, but yields no machine-usable public source content:
empty or parked/placeholder pages, sitemap without usable entries, or
content that fails the frozen keyword/official-domain gates without the
runtime being wrong.

### SUCCESS
Normal usable source.

## Adjudication rules

1. Availability is adjudicated independently of the runtime's route
   outcome (Section 10). "Runtime found nothing" is never evidence of
   unavailability.
2. A case may leave the available-source denominator only if the probe
   evidence independently supports one of: SOURCE_HTTP_UNAVAILABLE,
   SOURCE_RENDER_UNAVAILABLE, SOURCE_DNS_UNAVAILABLE, or
   SOURCE_CONTENT_UNUSABLE for the relevant authoritative host.
3. If the relevant authoritative host was reachable but the runtime
   probed a different host because of a pattern/implementation defect,
   the case is RUNTIME_FAILURE_OR_UNRESOLVED (Section 14, criterion 4).
   Frozen-code provenance of the defect changes nothing: the certification
   question is whether the candidate can be certified, not who is to
   blame.
4. Relevant-host determination for Raelingen: the frozen V2.3 benchmark
   corpus gold URLs define the authoritative hosts (all nine:
   ralingen.bedreinnsats.no). Runtime attempt logs define which hosts the
   runtime actually probed.
5. Probe protocol (bounded, burned hosts only): OS DNS lookup; direct
   HTTP GET with the frozen runtime user agent
   (Mozilla/5.0 (compatible; NAVExploreDiscovery/1.0; research)) and the
   frozen 15 s timeout; headless-Chrome render probe only where the
   frozen runtime itself would render (SPA shell (200, "")); body
   sha256 + size + timestamps recorded; no external search; no new
   municipalities; no retries beyond one identical re-probe for
   intermittent-DNS confirmation.
6. Every probe result is recorded with raw evidence in
   source-availability-results.json. No case-specific exceptions are
   created (Section 9).

## General failure behavior (Section 12)

The taxonomy is tested for generality against at least three additional
burned failure/error fixtures from earlier frozen artifacts (transport
failure, 403 challenge, legitimate empty) before it is applied to the
nine Raelingen cases.
