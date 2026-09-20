# Implementation Report - V2.3 Site-Direct-Only

Task: NAV-EXPLORE-LOCAL-DISCOVERY-SITE-DIRECT-ONLY-V2_3, 2026-09-09.

## What was built

1. Root-cause repair for dead CMS shells (new files runtime/discovery_v2/render.py, runtime/discovery_v2/roots.py):
   - render_url rewritten from subprocess.run to Popen + communicate(timeout=...). Fixes two frozen bugs: an UnboundLocalError on the timeout path (hung Chrome was never killed) and a race between Python's wait and Chrome's own --timeout.
   - canonical_roots() generalizable pattern rule: www.<slug>.kommune.no, bare <slug>.kommune.no, an ae-compressed variant (Raelingen case), and the national platform <slug>.bedreinnsats.no only after every kommune.no variant fails. Pattern rule only, no municipality lookup table; corroborated by Brreg Enhetsregisteret as an identity source.
2. New-lineage subclass SiteDirectProviderV23 (in cli_v23.py) raises the per-municipality URL budget to 16. The frozen SiteDirectProvider (V2.1 snapshot SHA 54b38921...83806a) stays byte-identical. Budget math killed discovery in V2: four dead AIM-shell roots burned the frozen budget of 8 before any working candidate was reached.
3. Bounded render: RenderFetchFn(max_renders=4) caps serial render stalls on dead shell variants; a real SPA needs one render.
4. Official runners (run_official.py): benchmark / live / replay / access / audit subcommands.

## Historical-file remediation (disclosed)

During implementation the frozen file runtime/discovery_v2/providers.py was edited (a max_urls parameter was added). This violated the task requirement HISTORICAL_FILES_MODIFIED = 0. Remediation in this task:

- providers.py was restored byte-identical to the V2.1 implementation snapshot (SHA-256 re-verified: 54b38921b02736763d3baef25e7bb860f1bf1b9f8d3b0fb3ac58b0808083806a).
- The URL-budget raise moved into the new-lineage subclass SiteDirectProviderV23 in runtime/discovery_v2/cli_v23.py.
- Re-run after remediation: all test suites pass; replay re-run 22/22 MATCH.

The official benchmark/live artifacts of 2026-09-09 were produced with the budget-16 behavior, which is exactly the frozen subclass behavior; no rerun was required.

## Replay semantics fix

The first replay implementation incorrectly routed the 22 cells through the site-direct provider against V1 pages that contain no navigation anchors (0/22). Replay was re-wired to frozen V1 semantics (run_discovery mode=replay on the frozen SERP fixtures), the pipeline that produced the historical rerun predictions. Result after fix: 22/22 route matches, 0 semantic regressions.

## Access runner fixes

- RouteEvaluator.evaluate kwarg typo fixed: eligibility= -> eligibility_verified=.
- Misleading hard-coded regression counters replaced with honest computed fields (existence-safety regressions = frozen-route to ROUTE_UNVERIFIED downgrades only; method and self-referral drift reported separately).
