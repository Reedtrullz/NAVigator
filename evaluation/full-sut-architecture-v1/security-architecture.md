# Security Architecture

The SUT inherits the frozen security components and adds pipeline-level
boundaries. Nothing here redesigns discovery security; it reuses it.

## Reused frozen components

| Threat | Component | Notes |
|---|---|---|
| SSRF / local-private IP | runtime/discovery/security.py validate_url | Blocks private ranges, localhost, non-http(s); used by the discovery adapter for every URL. |
| Redirect abuse | discovery runtime fetch provider | Bounded redirects per frozen provider config; re-validated through validate_url per hop. |
| Response size / timeout | discovery provider config | Frozen bounds; adapter passes them through, never widens them. |

## Pipeline-level boundaries (new, Phase 2-3)

| Threat | Boundary |
|---|---|
| Malicious webpage text / prompt injection | External source content is DATA (ADR-006): retrieval + discovery outputs enter the pipeline as evidence objects with verbatim spans, never as instruction-bearing text into any prompt. Phases 1-3 have no LLM stage; if an LLM stage is added later, retrieved text is embedded as quoted data with an explicit data-only framing and span validation, and the deterministic pipeline remains authoritative. |
| Source trust | authority_level comes from source classification (LAW / NATIONAL_GUIDANCE / MUNICIPAL_SOURCE / INTERNAL_DOC), never from the page's own claims about itself. Conflicts are recorded, higher authority wins (provenance-contract.md rule 2). |
| Path/file injection | Knowledge layer reads only the frozen manifest's artifact paths; user input never composes file paths. Rules registry reads only data/rules-v1.json. |
| Secrets | The SUT needs no secrets. Runner/adapter never read env credentials; discovery in replay mode needs none, live mode uses the discovery runtime's existing config path without exposing values to the SUT. |
| Corpus gold leak | Loader guard + harness self-test (corpus-loader-design.md). |
| Output injection into measurement lanes | Answer rendering quotes verbatim spans only; no raw external HTML/text is concatenated into the answer outside span quotes. |

## Input trust levels

| Input | Trust | Validation |
|---|---|---|
| user_query | untrusted | Length cap, normalization; never executed, never used as path/URL. |
| profile.age | untrusted | Integer 0-120; invalid -> triage/routing degrade to uncertainty, no crash. |
| location_context | untrusted | Matched against the frozen municipality registry; no match -> UNVERIFIED locality, never a guessed match. |
| knowledge artifacts | trusted, frozen | Read-only, SHA-pinned at index build. |
| discovery content | untrusted data | validate_url + span extraction; drives only evidence, never control flow. |

## Denial-of-service bounds

Per case: bounded stages (S1-S11), bounded discovery levels (frozen protocol
levels 0-5), bounded retrieval candidates per track, bounded answer size. No
recursive discovery inside the SUT; the frozen runtime already bounds depth
and pages.

## Security tests (Phase 2-3, listed here; test-strategy.md owns the plan)

1. SSRF probe URLs in synthetic discovery fixtures are rejected by
   validate_url before fetch.
2. A fixture page containing instruction-like text produces evidence spans
   only; no pipeline stage treats it as instruction (assertable because the
   pipeline is deterministic and span-based).
3. Path traversal strings in user_query/location_context produce no file
   access (manifest-only reads).
4. Gold-leak probe case with gold-shaped keys planted in utterance/context
   fields does not trip the loader guard (guard checks structure, not text)
   and gold-shaped text in the query never reaches claims as fact.
