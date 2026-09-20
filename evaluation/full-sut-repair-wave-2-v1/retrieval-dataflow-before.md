# RC-08 retrieval dataflow (pre-repair, evidence-backed)

Task: NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1. All observations below are
structural probes of the live Wave-1 source tree, not measurement outcomes.

## Frozen retrieval chain

    S3 decompose -> tracks[] (domain each)
    -> S4 s4_knowledge_retrieval (phase2/pipeline.py)
       for each track: retrieve(query, track.domain)
       then OVERWRITES rec["domain"] = track["domain"]
    -> S6/S7/S8 consume _s4_records
    -> S9 planner emits one INFO block per _s4_records entry
    -> renderer prints "Nasjonal informasjon:" per INFO block

## Proven defect A: doc scoring ignores track domain (PROVEN)

runtime/sut/phase2/knowledge.py retrieve() filters FROZEN_RULEs by
RULE_DOMAINS but scores EVERY doc in data/knowledge-index-v1.json (61 docs,
no domain field) for every track query. A mental_health track can therefore
return PROJECT_RESEARCH spans from housing/financial/legal docs (e.g. doc 48
barnebidrag, doc 55 bostotte, doc 37 foreldretvist) when keywords collide.

## Proven defect B: _doc_record hardcodes domain "general" (PROVEN)

_doc_record() emits "domain": "general" for all doc records. Consequences:

1. S8 derive_track_state(knowledge=[k for k in _s4_records if
   k["domain"] == entry["domain"]]) sees an EMPTY knowledge list for any
   non-general track: doc records are invisible to track epistemics.
2. build_national_route_candidates skips every doc record only when its
   claim lacks a quoted/bold name; domain gating is dead.
3. The pipeline-level overwrite in s4 (defect C) hides (1) and (2) at
   runtime but not inside retrieve() itself.

## Proven defect C: s4 overwrites every record domain (PROVEN)

phase2/pipeline.py s4_knowledge_retrieval sets rec["domain"] = track.domain
for every retrieved record. A housing-track copy of the same rule record
keeps its mental_health identity nowhere; the FROZEN_RULE mental_health rule
is re-labelled housing for the housing track. Contaminated records are
indistinguishable from track-native evidence downstream.

## Proven defect D: planner emits INFO blocks for every record (PROVEN)

phase3/planner.py emits one INFO block per _s4_records entry with no track
filter. With up to 5 records per track and multiple tracks, the answer
renders "Nasjonal informasjon:" blocks from domains irrelevant to the
track(s). This is the 104/120 unscoped-national-block mechanism identified
in the frozen post-Wave1 analysis.

## Defect E: renderer prints INFO blocks verbatim (structural, same stage
as D; repair is at planner scope, no renderer change needed)

## Defect F: knowledge index carries no domain metadata (PROVEN)

data/knowledge-index-v1.json docs have only id/path/sha256/class/
freshness_class. There is no per-doc domain to filter on. The repair must
extend the index with honest per-doc domain arrays. Note: the index is an
frozen artifact manifest; adding a non-content field does not change doc
sha256 pins (load_knowledge verifies the FILE sha, not the index entry).

## Defect G: gap-doc reserve keeps irrelevant gap records (structural)

The gap slot is reserved per track query regardless of domain; a
mental_health query can pull the kunnskapshullregister best-span even when
the span matches keywords only because they occur in an unrelated gap
entry. Domain filtering must apply to gap docs too (they keep their
GAP/uncertainty class; only scope changes).

## Repair contract (RC-08)

1. Index gains "domains": [..] per doc from the frozen decompose vocabulary
   (mental_health, housing, financial_support, child_safety, education,
   employment, legal_rights) plus "general" only where genuinely generic.
2. retrieve(): docs whose domains exclude the track domain are not scored.
3. _doc_record() emits the doc's domains; single-domain selection uses the
   record's own domains (source truth), not the track label.
4. s4 stops overwriting rec["domain"]; records keep source identity.
5. Planner INFO blocks are scoped to records whose domains include the
   active track domain.
6. FROZEN_RULE/RULE_DOMAINS and GAP_DOC_IDS behavior unchanged.

Hard gate: UNSCOPED_CROSS_TRACK_EVIDENCE_INJECTION = 0 in deterministic
fixtures (a mental_health track must never render evidence whose source
domains exclude mental_health).
