# Provenance Contract

Every claim and route in SUT output traces to at least one provenance record.
No provenance = claim must not be asserted (it may only appear inside
uncertainty_expressed).

## Provenance record (canonical shape)

Mirrored in decision-context.schema.json and sut-output.schema.json:

| Field | Type | Meaning |
|---|---|---|
| id | string (P1, P2, ...) | Stable within one SUT output. |
| source_type | enum | KNOWLEDGE_ARTIFACT, DISCOVERY_PAGE, RULE_REGISTRY, STRUCTURED_SOURCE, ERROR_STATE. |
| source_ref | string | URL for web sources; repo-relative path for artifacts; rule id for the rules registry. |
| retrieved_at | string/null | When the content was fetched (discovery pages); null for pre-frozen artifacts. |
| verified_at | string | When the SUT verified/loaded the content for this execution. |
| claim_supported | string | The claim this record supports (one line). |
| evidence_span | string/null | Verbatim span from the source. Must be a substring of source content and of the rendered answer when quoted. |
| authority_level | enum | LAW, NATIONAL_GUIDANCE, MUNICIPAL_SOURCE, INTERNAL_DOC, UNKNOWN. |
| freshness_class | enum | CURRENT, STALE, NEEDS_REVALIDATION, POINT_IN_TIME. |
| conflicts_with | list of ids | Declared conflicts with other provenance records. |
| chain_parent_id | string/null | Parent record when this evidence was reached through another source (discovery link chain). |

## Rules

1. Verbatim spans only. evidence_span values are exact substrings of the
   source content; paraphrase is recorded in the claim, never in the span.
2. Authority ordering: LAW > NATIONAL_GUIDANCE > MUNICIPAL_SOURCE >
   INTERNAL_DOC. Conflicts resolve toward higher authority; the conflict is
   recorded, never silently dropped.
3. Discovery pages carry the full chain: the page record has chain_parent_id
   pointing at the hub/navigation page it was reached from when applicable.
4. ERROR_STATE records document absence: when discovery fails, a provenance
   record of type ERROR_STATE with the failure state supports the uncertainty
   claim ("could not verify"), never a negative existence claim.
5. Freshness: knowledge artifacts are POINT_IN_TIME with the verification date
   recorded; discovery results re-verified in the same execution are CURRENT.
   STALE content (older than the freshness policy in execution-harness
   design) requires NEEDS_REVALIDATION and an uncertainty entry.
6. IDs are assigned in stage order (S4 before S5 before S6) and never reused.

## Who writes provenance

- S4 knowledge retrieval: KNOWLEDGE_ARTIFACT + RULE_REGISTRY records.
- S5 discovery: DISCOVERY_PAGE (+ ERROR_STATE on failure), reusing the
  provenance graph emitted by the frozen discovery runtime.
- S6 route reasoning: creates no new sources; it references existing records.
- S7 aggregation: deduplicates and wires conflicts_with.
