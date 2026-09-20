# PROTOCOL-PROVIDER COMPATIBILITY AUDIT

Dato: 2026-09-09 03:55 UTC. Kilde: data/local-service-discovery-protocol-v1.json (SHA fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca).

Protokollen definoerer syv discovery-teknikker: KNOWN_PAGE_CONTENT, NAVIGATION_LINK, SITE_SEARCH, SITEMAP, QUERY_SEARCH, INTERMUNICIPAL_CHAIN, OFFICIAL_EXTERNAL_PORTAL.

| Execution path | Vurdering | Protokollgrunnlag |
|---|---|---|
| A. Direct municipality landing/service discovery | EXPLICITLY ALLOWED | Teknikk KNOWN_PAGE_CONTENT; level 1 satisfaction_note: known URL under catalog path satisfies level 1 |
| B. Municipality internal search/service catalog | EXPLICITLY ALLOWED | Teknikk SITE_SEARCH; level 3 STRUCTURED_MUNICIPALITY_SEARCH: internal search engine, document index, service catalog search |
| C. Navigation/link traversal | EXPLICITLY ALLOWED | Teknikk NAVIGATION_LINK; level 2 SERVICE_DESCENDANTS med provenance-krav per kant |
| D. Sitemap discovery | EXPLICITLY ALLOWED | Teknikk SITEMAP; level 3; tom/failende sitemap skal logges som rejected source |
| E. External web search | EXPLICITLY ALLOWED | Teknikk QUERY_SEARCH (query families level 1-2); forblir tillatt som utskiftbar capability/fallback |
| F. Rendered-page fallback | IMPLICITLY COMPATIBLE | Ikke spesifisert i doctrine; fetch-mekanisme, ikke discovery-teknikk. V1-runtime detekterer allerede RENDER_REQUIRED og rapporterer aerlig. Adapter er fetch-lag, endrer ikke levels/stop-states/evidence-krav |

## HARD PROTOCOL GATE (paragraph 4)

Resultat: **INGEN GAP**. En kompositt-providerarkitektur (site-direct foerst, external search som utskiftbar fallback) kan implementeres innenfor gjeldende discovery-doktrine: alle stier eksisterer allerede som protokollteknikker, og provider-sammensetning er execution semantics, ikke discovery semantics. PROTOCOL_V1_PROVIDER_CONTRACT_GAP utloeses ikke.

## Begrensninger som maa respekteres i V2

- Query families forblir de 9 frosne malene; ingen nye semantiske search-begreper.
- Sitemap/interne soek er level 3; site-direct landing/catalog er level 0-2; rekkefoelgen i compositen maa reflektere level-prioritering, ikke omdefinere den.
- Search-resultater/snippets forblir DISCOVERY evidence; final route authorization krever hentet offentlig source page.
- Empty/failende sitemap og soek skal logges som rejected source (level 3-note).
