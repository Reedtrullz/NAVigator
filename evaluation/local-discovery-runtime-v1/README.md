# Local Discovery Runtime Prototype V1

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-PROTOTYPE-V1
Status: READY_FOR_FRESH_EVAL (development candidate; not certified, not blind-tested)
Date: 2026-09-09

## What This Is

A replay-first, rule-based runtime implementation of the frozen discovery protocol
`data/local-service-discovery-protocol-v1.json` (SHA `fb533d99...`). It discovers
municipal psychological-health service pages, extracts access evidence, classifies
per the ACCESS-E1..E5 doctrine, and produces a canonical route state with full
provenance. No LLM anywhere in the control flow.

## Quick Start

Replay (deterministic, offline):

    python3 -m runtime.discovery.cli --municipality "Bamble" --age 22 --mode replay

Tests (stdlib unittest):

    python3 -m unittest runtime.discovery.tests

## Layout

- `runtime/discovery/` - runtime (planner, providers, extractor, classifier, orchestrator, schema validator, CLI)
- `data/local-discovery-runtime-result-v1.schema.json` - frozen result contract
- `fixtures/` - replay fixture manifest + build script
- `replay-results.json` - 22-cell replay matrix vs frozen predictions (21/22)
- `access-regression-results.json` - T1-T9 real-replay regression (5/9 exact, 4 FIXTURE_INCOMPLETE, doctrine 9/9)
- `determinism-check.json` - 3x byte-identical runs per municipality
- `live-smoke-results.json` - bounded live smoke (fetch 3/3; search backends bot-blocked)
- `protocol-gap-log.json`, `security-report.md`, `test-report.md`, `source-integrity.md`, `final-report.md`

## Architecture (one paragraph)

DiscoveryPlanner generates levels 0-5 from the frozen protocol; Replay/Http providers
abstract search and fetch; LinkExplorer follows official-domain links with depth/page
bounds; ServiceExtractor produces fail-closed evidence markers (phone, email, form,
drop-in, referral polarity, age bounds, target group); AccessClassifier maps markers to
canonical access methods + self_referral per E1-E5; RouteEvaluator produces the canonical
route state; ProvenanceGraph records every discovery edge; ResultSerializer emits
byte-stable canonical JSON validated against the result schema.

