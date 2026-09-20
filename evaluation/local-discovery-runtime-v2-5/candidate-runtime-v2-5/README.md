# LOCAL-DISCOVERY-RUNTIME-V2.5 (frozen development candidate)

Status: LOCAL_DISCOVERY_RUNTIME_V2_5_CANDIDATE_FROZEN
Architecture: DISCOVERY_FALLBACK_V25
Candidate SHA-256 (manifest.json): see hashes.txt line 1.

New lineage built on the frozen V2.4 base. Frozen V2/V2.3/V2.4 files are
reused byte-identically (verified by SHA comparison against the V2.4
manifest); V2.5 adds:

- SiteDirectProviderV25: bounded sitemapindex child-follow
  (SITEMAP_INDEX_FOLLOW) and one bounded render-on-empty navigation
  extraction (RENDERED_NAVIGATION_LINK), both fail-closed, with the
  V23-parity URL budget (16).
- classification_gate_v25: service-specific URL gate (generic section
  pages cannot claim FULLY_VERIFIED; capped to ACCESS_PARTIAL).
- orchestrator_v25: verbatim copy of the frozen orchestrator with three
  documented deltas (name, discovery_v2_5 runtime field, V25 evaluator).

Validation (burned data only, one run each, fresh process):
- Raelingen gate: 9/9 SUCCESS (NAVIGATION_LINK, correct platform root).
- Full benchmark: 117/117 SUCCESS, gold-domain recall 1.0,
  official domain precision mean 0.9692, 0 bot blocks, 0 provider errors.
- Replay: 22/22 MATCH.
- Live (13 municipalities): 13/13 COMPLETE, 0 runtime failures,
  0 external search calls; Bamble FV correctly capped to ACCESS_PARTIAL.
- Access regression: 7/9 with the two documented V2.3 source-drift pairs
  (Alta T2, Hasvik T9); 0 existence-safety regressions.
- Network audit: external_search_calls=0.
- Tests: tests_v25 7/7; frozen suites tests/tests_v21/tests_v22/
  tests_v23/tests_v24 all green after the budget-parity fix.

Boundaries: no fresh municipalities, no fresh eval, no new blind set,
no external search providers, no Protocol V1 change (SHA fb533d99...
f99ca verified in the benchmark artifact). This is a development
candidate, not a generalization claim; the next step is a separately
tasked fresh holdout.
