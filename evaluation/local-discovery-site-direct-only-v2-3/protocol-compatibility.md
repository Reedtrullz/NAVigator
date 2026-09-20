# Protocol V1 Compatibility Gate (Gate A) - V2.3 Site-Direct-Only

Question (task section 3): can the discovery protocol complete correctly with
site-direct / internal-navigation / sitemap / render paths, without external
web search as a mandatory semantic step?

## Verdict: OPTIONAL CAPABILITY

External web search can be used, but it is NOT required for protocol
completion. No PROTOCOL_V1_REQUIRES_EXTERNAL_SEARCH stop applies.

## Evidence (data/local-service-discovery-protocol-v1.json)

Protocol SHA-256 (verified before any code change):

```
fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca
```

1. **Discovery levels are site-anchored, not search-anchored.** The frozen
   levels are 0 KNOWN_SERVICE_URL, 1 MUNICIPALITY_SERVICE_CATALOG,
   2 SERVICE_DESCENDANTS, 3 STRUCTURED_MUNICIPALITY_SEARCH ("Sitemap,
   internal search engine, document index, service catalog search"),
   4 INTERMUNICIPAL_DISCOVERY, 5 OFFICIAL_EXTERNAL_ENTRY. External *web
   search engines* are not a protocol level; level 3 refers to search
   mechanisms on the municipality's own site.
2. **QUERY_SEARCH is a technique, not a stage.** The frozen
   discovery_techniques list contains QUERY_SEARCH, but techniques are
   implementation choices, not required steps. query_family_note states:
   "Templates, not engine-specific requirements. Any search implementation
   must log the query strings actually used."
3. **Terminal state PUBLIC_DATA_EXHAUSTED is defined by level coverage, not
   by engine use.** Frozen stop-state definition: "All preregistered levels
   checked without establishing access. No infinite search." The frozen
   false_no_match_rule requires the protocol to be "executed to a terminal
   state"; site-direct levels 0-3 are part of that execution.
4. **Source hierarchy keeps private/SEO sources out of evidence anyway:**
   "private/SEO sources are discovery hints only and never final evidence."
   Removing the external engine removes at most a discovery-hint channel.
5. **Frozen V2.1/V2.2 behavior already demonstrated completion without
   external search**: site-direct benchmark execution 117/117 and
   gold-domain recall 117/117; live burned 13/13 with
   external_fallback_used = false on all 13 runs.

## Required levels attempted before PUBLIC_DATA_EXHAUSTED (V2.3 invariant)

The runtime site-direct provider attempts, in order: canonical root (level
0/1 anchor), keyword navigation links (level 1/2), sitemap.xml (level 3).
The orchestrator counts execution as DISCOVERY_INCOMPLETE when no page could
be fetched, and uncertainty falls back to NO_VERIFIED_ROUTE_AFTER_PROTOCOL
only through the frozen terminal-state logic. The V2.3 test suite adds an
explicit invariant that a legitimate NO_RESULTS terminal requires the
attempt log to show root+sitemap steps, i.e. exhaustion is not authorized by
a single failed fetch.

## Notes

- Rendered-page fallback is a fetch mechanism for the same public pages,
  not a new semantic step.
- Municipality-root resolution without a search engine is documented in
  implementation-report.md (canonical registry + canonical URL pattern),
  per task section 20.

