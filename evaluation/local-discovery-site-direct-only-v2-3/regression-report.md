# Regression Report - V2.3 Site-Direct-Only

## Replay (frozen V1 fixtures, 22 cells)

22/22 route matches, 0 semantic/route regressions, 0 critical false-no-route, 0 unsupported FULLY_VERIFIED. Historical Askoy behavior preserved (2x ROUTE_FULLY_VERIFIED, pages_fetched=2).

Note: the first replay attempt (0/22) was a runner bug - it routed replay cells through the site-direct provider against anchor-less fixture pages. Fixed by re-wiring replay to frozen V1 semantics; see implementation-report.md.

## Access regression (9 burned targets, live fetch)

7/9 route matches. The 2 mismatches were inspected against current page content and classified as external content drift, not runtime regression:

- T2 Alta (ROUTE_FULLY_VERIFIED -> ROUTE_EXISTENCE_ONLY): the live page no longer carries the age/target-group text that grounded eligibility at V1 freeze; self-referral markers (phone, e-mail, explicit self-contact) are still present. The conservative downgrade is correct per frozen doctrine.
- T9 Hasvik (ROUTE_EXISTENCE_ONLY -> ROUTE_FULLY_VERIFIED): the live page now documents children and young people 0-20 years plus e-mail contact and a GP-referral requirement. The upgrade is grounded in current page evidence.

No existence-safety regressions (0 frozen-route to ROUTE_UNVERIFIED downgrades). Method drift on 4 cells (live pages list more contact channels than at freeze); reported, not scored as regression.

## Live burned (13 municipalities)

12/13 COMPLETE (gate: at least 12), Raelingen DISCOVERY_INCOMPLETE with honest failure semantics (external site migration; see final-report.md). runtime_failures=0, bot_block=0, critical_false_no_route=0, unsupported_fully_verified=0, external_search_calls=0.

## Benchmark (117 burned queries)

117/117 executed, 108/117 SUCCESS (92.31 percent), gold-domain 108/117, 0 bot-blocks, 0 provider errors. The 9 failures are exactly the 9 Raelingen queries (Q-raelingen-1..9).

## Test suites

130 tests across V1/V2/V2.1/V2.2/V2.3: all pass (see test-report.md).
