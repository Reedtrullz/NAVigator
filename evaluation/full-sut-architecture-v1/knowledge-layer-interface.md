# Knowledge Layer Interface

The SUT reads the existing NAV Explore knowledge base as data. Markdown files
are not hardcoded into business logic; the layer is an index + loader.

## Corpus classes

| Class | Examples | Freshness | Use |
|---|---|---|---|
| STABLE_LEGAL | 18-lovverk-og-rettigheter.md, 63/64/68 (overgangsstonad), 35 (foreldreansvar) | LAW/NATIONAL_GUIDANCE authority; POINT_IN_TIME with verification date | Legal claims, deadlines, eligibility framing |
| DECISION_SUPPORT | 26-beslutningsstotte-hvor-henvende-seg.md, 28b-18-20-aar-routing.md, 28c-beslutningsstotte-gaps.md, 45-beslutningstre-hvem-ringer-jeg.md | CURRENT (frozen verification pass) | Route candidates, referral paths, routing tables |
| SERVICE_CATALOG | 25-kommunale-psykiske-tjenester-barn-unge.md, 31-skolehelsetjenesten.md, 28-ppt-i-dybden.md | NATIONAL service descriptions | Service semantics, scope, exclusions |
| LOCAL_DISCOVERY_PROTOCOL | 73-lokal-tilgang-og-discovery-protokoll-v1.md, 74-lokal-discovery-generalisering-v1.md, runtime protocol JSON | Frozen protocol | Discovery configuration only |
| HISTORICAL_RESEARCH | 71, 72, 44, 47, 61 (case/scenario docs) | POINT_IN_TIME | Background; never sole authority for a route claim |
| GAP_REGISTER | 69-kunnskapshullregister.md, 28c | CURRENT | Fail-closed: known gaps become uncertainty entries, not silently skipped |
| SOURCE_DOCUMENTATION | 24, 27, 46, 53, 62 (kildedokumentasjon) | POINT_IN_TIME | Provenance chain backing |

## Loader contract (product-side module runtime/sut/knowledge.py, Phase 2)

    load_index() -> KnowledgeIndex
    query(index, track) -> list[KnowledgeEvidence]

KnowledgeIndex: manifest of artifacts with path, class, title, freshness
class, verification date. Built from the repo file list + INNHOLD.md
metadata at index-build time; the manifest is frozen data, not code.

KnowledgeEvidence:

| Field | Type |
|---|---|
| artifact_path | string (repo-relative) |
| section | string/null |
| span | string (verbatim) |
| authority_level | LAW / NATIONAL_GUIDANCE / MUNICIPAL_SOURCE / INTERNAL_DOC |
| freshness_class | CURRENT / STALE / NEEDS_REVALIDATION / POINT_IN_TIME |
| topic_tags | list[string] |

## Query semantics

1. Retrieval is deterministic: topic-tag + keyword match over the frozen
   manifest; scoring is simple and auditable (no embeddings in Phases 1-3).
2. Spans are verbatim substrings of the artifact; extraction records line
   offsets so provenance can cite section.
3. GAP_REGISTER content flows into uncertainty_expressed, never into claims.
4. HISTORICAL_RESEARCH may support background claims only; route claims need
   DECISION_SUPPORT or SERVICE_CATALOG or live discovery evidence.

## Structured rules registry

Hard legal deadlines and deterministic eligibility (age gates, statutory
frist-dager) live in a new frozen data file data/rules-v1.json, seeded from
the already-verified knowledge artifacts (65-virkedager under 23, 10-virkedager
vurderingsfrist, akutte safety routes). Format:

    {
      "rule_id": "R-PRI-4A-65D",
      "statement": "...",
      "authority_level": "NATIONAL_GUIDANCE",
      "source_refs": ["25-kommunale-psykiske-tjenester-barn-unge.md#..."],
      "applies_when": {"age_lt": 23, "domain": "mental_health"},
      "kind": "MAX_WAIT_DAYS",
      "value": 65
    }

S6 reads rules as data; the registry is the only source for deterministic
eligibility arithmetic. Rules are frozen and SHA-pinned like other data.
