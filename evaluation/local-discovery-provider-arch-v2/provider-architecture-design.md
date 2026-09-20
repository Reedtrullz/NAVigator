# PROVIDER ARCHITECTURE DESIGN V2

Dato: 2026-09-09 03:55 UTC. Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-ARCH-V2.

## Problem

V1 binder runtime til en ekstern HTML-soekemotor (DDG) som er systematisk bot-blokka (1/10 queries). Soek er single-point-of-failure, selv om protokollen allerede tillater fire andre teknikker.

## Maalarkitektur

DiscoveryProvider (contract V2)
  - SiteDirectProvider: level 0-3 root, catalog, nav, sitemap, internal search
  - ExternalSearchProvider: level 1-2 query families, utskiftbar backend
  - CompositeDiscoveryProvider: deterministisk frosen fallback-policy + health + fallback-logg

## Deterministic fallback order (fra protokollens level-prioritering)

1. Stage A - SiteDirect: canonical root/known catalog paths (level 0-1).
2. Stage B - SiteDirect structured: sitemap + internal search (level 3), navigation links (level 2).
3. Stage C - ExternalSearch fallback: frosne query families (level 1-2 QUERY_SEARCH) med utskiftbar backend.
4. Stage D - Fortsatt navigation/rendering iht. level semantics; rendered fallback kun i fetch-laget.

Hvert bytte logges i provider_chain (NO SILENT FALLBACK).

## Kontrakt

Se provider-contract-v2.schema.json. Kanoniske statuser: SUCCESS, NO_RESULTS, RATE_LIMITED, BOT_BLOCKED, AUTH_REQUIRED, PROVIDER_UNAVAILABLE, TIMEOUT, INVALID_RESPONSE, INTERNAL_ERROR. NO_RESULTS og BOT_BLOCKED blandes aldri.

## Health model

Hver provider rapporterer healthy/failure_class/successful_queries/attempted_queries. Runtime skiller 'soekte og fant ingenting' (NO_RESULTS) fra 'soekemotoren lot meg ikke soeke' (BOT_BLOCKED).

## Gjenbruk (NO SEMANTIC REWRITE)

AccessClassifier, RouteEvaluator, EvidenceLedger, ProvenanceGraph, DiscoveryPlanner-query-semantikk og security-module importeres fra runtime.discovery (V1). V2 endrer bare discovery/provider-laget.

## Provenance-invariant

Search-resultater er DISCOVERY evidence. FULLY_VERIFIED krever fortsatt hentet offentlig source page med content-hash. Testes eksplisitt.
