# Implementation plan - Local Discovery Runtime Prototype V1

**Task ID:** NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-PROTOTYPE-V1
**Dato:** 2026-09-09
**Autoritativ protokoll:** data/local-service-discovery-protocol-v1.json (SHA fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca, verifisert ved oppstart)

## Arbeidsgang (TDD der praktisk)

1. Runtime-pakke under runtime/discovery/ med logisk separate komponenter (klassenavn f	olger spec: ProtocolLoader, DiscoveryPlanner, SearchProvider, FetchProvider, RenderedPageFallback, LinkExplorer, ServiceExtractor, EvidenceLedger, AccessClassifier, RouteEvaluator, ProvenanceGraph, ResultSerializer).
2. Tester (stdlib unittest, ingen ny avhengighet) skrives pr. modul og kj%res løpende før/integrering.
3. Replay-fixtures bygges fra allerede frosne artefakter (retained evidence-pages); fixture-manifest med SHA. Ingen kommunespifikke regler i runtime - runtime er generisk, fixtures er data.
4. Replay-kjøring mot 22 generalisering-celler + 9 access-targets; sammenligning mot frosne route-states.
5. Determinisme: 3 identiske replay-runs, byte-identisk normalisert output.
6. Live smoke på 3 allerede-forskede kommuner (enkel / navigasjon / SPA-fallback).
7. Rapporter + SHA-reverifikasjon.

## Modulplassering

- runtime/discovery/protocol.py - ProtocolLoader (load, SHA-validering)
- runtime/discovery/providers.py - SearchProvider (HtmlSearch/ReplaySearch), FetchProvider (HttpFetch/ReplayFetch), RenderedPageFallback-grensesnitt
- runtime/discovery/security.py - URL/SSRF-beskyttelse (kun http/https, offentlige IP-er, ingen redirects til private nett)
- runtime/discovery/engine.py - DiscoveryPlanner, LinkExplorer, ServiceExtractor, EvidenceLedger, AccessClassifier, RouteEvaluator, ProvenanceGraph, orkestrering (run_discovery)
- runtime/discovery/serialize.py - ResultSerializer (normalisert, byte-stabil JSON)
- runtime/discovery/cli.py - CLI (--mode replay|live, --municipality, --municipality-number, --age, --need)
- runtime/discovery/tests.py - unittest-suite

## Viktige designvalg

- Deterministisk kjerne: ingen LLM i control flow. Ekstraksjon er regelbasert (regex/markører) med fail-closed: manglende bevis gir lavere route-state, aldri høyere.
- Self-referral holdes separat (YES/NO/CONDITIONAL/UNCLEAR); telefon infererer aldri alene self_referral=YES (ACCESS-E3). Generisk switchboard-telefon gir ikke access (ACCESS-E2) - telefonen må være koblet til tjenesten på siden.
- Aldersmatching: scenario-alder må være dekket av eksplisitt dokumentert aldersspenn før eligibility kan verifiseres.
- False-no-match: ROUTE_UNVERIFIED først etter alle levels er kjørt til terminal state; runtime-feil gir DISCOVERY_INCOMPLETE-execution-status, aldri "ingen tilbud".
- PROTOCOL_MODIFICATIONS = 0; protokollhull logges i protocol-gap-log.json.
